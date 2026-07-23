"""
Pipeline de datos reproducible: politeia-pipeline-datos.

Cierra HUECO #5 (reproducibilidad) para el tramo enriquecido→validado→publicado
de vista_mapa, y REUBICA el gate de validación que hoy vive en deploy.yml (que
validaba la key live DESPUÉS de publicarla — tarde). Acá se valida en _staging
ANTES de publicar: una subida mala nunca llega a producción.

Flujo (Step Functions Standard):

    Normaliza ─▶ Valida ─▶ ¿ok? ─┬─ sí ─▶ Publica (copia _staging→live) ─▶ Publicado
                                  └─ no ─▶ Alerta (SNS) ─▶ Rechazado (Fail)
    (cualquier error de ejecución en Normaliza/Valida ─▶ AlertaError ─▶ FalloEjecucion)

Piezas:
  - Layer `politeia-core`: empaqueta `core/` (esquema, validadores, familias) como
    única fuente de verdad compartida por las dos Lambdas.
  - Lambda `politeia-normaliza-familias` (liviana, csv+core): _source → +familia → _staging.
  - Lambda `politeia-valida-dataset` (pandas del layer gestionado): valida _staging.
  - SNS `politeia-alertas`: notifica el rechazo/fallo (suscribir el email a mano).

ALCANCE HONESTO (CLAUDE.md §2): cubre enriquecer+validar+publicar. NO reconstruye
el paso consolidado→vista_mapa base (eso lo deja upstream en `_source/`).
"""
import os
import shutil

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_sns as sns,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
from constructs import Construct

# --- Claves S3 del pipeline -------------------------------------------------
# _source y _staging quedan como HERMANOS de vista_mapa/ (no adentro) a propósito:
# el crawler de Glue (data_stack) apunta a `.../vista_mapa/`, así no levanta estas
# keys de trabajo como tablas sucias.
SOURCE_KEY = "electoral/procesados/_source/vista_mapa.csv"      # entrada: base upstream
STAGING_KEY = "electoral/procesados/_staging/vista_mapa.csv"    # candidata (se valida acá)
LIVE_KEY = "electoral/procesados/vista_mapa/vista_mapa.csv"     # publicada (solo si valida OK)

# Layer gestionado de AWS SDK for pandas (py3.12, us-east-1). La cuenta 336392948345
# es de AWS. Verificar/actualizar la versión con la doc oficial:
#   https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html
# (v29 confirmada disponible en us-east-1 al 2026-07-23).
PANDAS_LAYER_ARN = (
    "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:29"
)


def _stage_core_layer() -> str:
    """Copia `core/` al layout que Lambda espera para un layer (`python/core/`).

    Devuelve la ruta de la carpeta a empaquetar. Sin Docker, sin duplicar fuente
    en el repo (el destino está en infra/.build/, gitignoreado). Se ejecuta en
    cada `cdk synth`, así el layer siempre refleja el `core/` actual.
    """
    here = os.path.dirname(os.path.abspath(__file__))       # infra/stacks
    infra_dir = os.path.dirname(here)                        # infra
    repo_root = os.path.dirname(infra_dir)                   # raíz del repo
    core_src = os.path.join(repo_root, "core")
    layer_root = os.path.join(infra_dir, ".build", "layer-core")
    core_dst = os.path.join(layer_root, "python", "core")

    if os.path.isdir(layer_root):
        shutil.rmtree(layer_root)
    shutil.copytree(
        core_src,
        core_dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "requirements.txt"),
    )
    return layer_root


class PipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        data_bucket_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Layer compartido con el core (esquema/validadores/familias) -----
        core_layer = lambda_.LayerVersion(
            self,
            "CoreLayer",
            layer_version_name="politeia-core",
            code=lambda_.Code.from_asset(_stage_core_layer()),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
            description="core/ de POLITEIA (esquema, validadores, familias) como layer",
        )
        pandas_layer = lambda_.LayerVersion.from_layer_version_arn(
            self, "PandasLayer", PANDAS_LAYER_ARN
        )

        common_env = {
            "DATA_BUCKET": data_bucket_name,
            "SOURCE_KEY": SOURCE_KEY,
            "STAGING_KEY": STAGING_KEY,
        }

        # --- Lambda 1: normaliza (agrega familia) → _staging ----------------
        norm_logs = logs.LogGroup(
            self,
            "NormalizaLogs",
            log_group_name="/aws/lambda/politeia-normaliza-familias",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )
        fn_normaliza = lambda_.Function(
            self,
            "Normaliza",
            function_name="politeia-normaliza-familias",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../ingest/normaliza"),
            layers=[core_layer],
            timeout=Duration.minutes(2),
            memory_size=512,
            log_group=norm_logs,
            environment=common_env,
            description="Lee _source, agrega columna familia (core) y escribe _staging",
        )
        fn_normaliza.add_to_role_policy(
            iam.PolicyStatement(
                sid="LeerSource",
                actions=["s3:GetObject"],
                resources=[f"arn:aws:s3:::{data_bucket_name}/{SOURCE_KEY}"],
            )
        )
        fn_normaliza.add_to_role_policy(
            iam.PolicyStatement(
                sid="EscribirStaging",
                actions=["s3:PutObject"],
                resources=[f"arn:aws:s3:::{data_bucket_name}/{STAGING_KEY}"],
            )
        )

        # --- Lambda 2: valida _staging (pandas + core) -----------------------
        val_logs = logs.LogGroup(
            self,
            "ValidaLogs",
            log_group_name="/aws/lambda/politeia-valida-dataset",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )
        fn_valida = lambda_.Function(
            self,
            "Valida",
            function_name="politeia-valida-dataset",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../ingest/valida"),
            layers=[core_layer, pandas_layer],
            timeout=Duration.minutes(3),
            memory_size=1024,       # pandas sobre ~3 MB de CSV
            log_group=val_logs,
            environment=common_env,
            description="Corre core/validadores.validar_vista_mapa sobre _staging (gate)",
        )
        fn_valida.add_to_role_policy(
            iam.PolicyStatement(
                sid="LeerStaging",
                actions=["s3:GetObject"],
                resources=[f"arn:aws:s3:::{data_bucket_name}/{STAGING_KEY}"],
            )
        )

        # --- SNS de alertas --------------------------------------------------
        topic = sns.Topic(
            self,
            "Alertas",
            topic_name="politeia-alertas",
            display_name="POLITEIA alertas",
        )

        # --- Definición del Step Functions -----------------------------------
        normaliza_task = tasks.LambdaInvoke(
            self,
            "PasoNormaliza",
            lambda_function=fn_normaliza,
            payload_response_only=True,
            comment="Enriquece familia y escribe _staging",
        )
        valida_task = tasks.LambdaInvoke(
            self,
            "PasoValida",
            lambda_function=fn_valida,
            payload_response_only=True,
            comment="Valida _staging (duros/blandos)",
        )

        publicar = tasks.CallAwsService(
            self,
            "Publica",
            service="s3",
            action="copyObject",
            parameters={
                "Bucket": data_bucket_name,
                "Key": LIVE_KEY,
                "CopySource": f"{data_bucket_name}/{STAGING_KEY}",
                "ContentType": "text/csv; charset=utf-8",
                "MetadataDirective": "REPLACE",
            },
            # CopyObject necesita GetObject (source) + PutObject (dest); el
            # iam_action autogenerado (s3:copyObject) no alcanza, se explicita.
            iam_resources=[f"arn:aws:s3:::{data_bucket_name}/{LIVE_KEY}"],
            additional_iam_statements=[
                iam.PolicyStatement(
                    actions=["s3:GetObject", "s3:PutObject"],
                    resources=[
                        f"arn:aws:s3:::{data_bucket_name}/{STAGING_KEY}",
                        f"arn:aws:s3:::{data_bucket_name}/{LIVE_KEY}",
                    ],
                )
            ],
            comment="Copia la candidata validada a la key live",
        )

        # Alerta de rechazo (validación con errores duros).
        alerta_rechazo = tasks.SnsPublish(
            self,
            "Alerta",
            topic=topic,
            subject="POLITEIA · pipeline de datos: dataset RECHAZADO",
            message=sfn.TaskInput.from_text(
                sfn.JsonPath.json_to_string(sfn.JsonPath.entire_payload)
            ),
        )
        # Alerta de error de ejecución (excepción en una Lambda).
        alerta_error = tasks.SnsPublish(
            self,
            "AlertaError",
            topic=topic,
            subject="POLITEIA · pipeline de datos: ERROR de ejecución",
            message=sfn.TaskInput.from_text(
                sfn.JsonPath.json_to_string(sfn.JsonPath.entire_payload)
            ),
        )
        alerta_error.next(sfn.Fail(self, "FalloEjecucion", error="ErrorDeEjecucion"))
        normaliza_task.add_catch(alerta_error, errors=["States.ALL"])
        valida_task.add_catch(alerta_error, errors=["States.ALL"])

        choice = sfn.Choice(self, "¿Pasa la validación?")
        definition = normaliza_task.next(valida_task).next(
            choice.when(
                sfn.Condition.boolean_equals("$.ok", True),
                publicar.next(sfn.Succeed(self, "Publicado")),
            ).otherwise(
                alerta_rechazo.next(
                    sfn.Fail(
                        self,
                        "Rechazado",
                        error="DatasetInvalido",
                        cause="La validación encontró errores duros; no se publica.",
                    )
                )
            )
        )

        sm_logs = logs.LogGroup(
            self,
            "PipelineLogs",
            log_group_name="/aws/states/politeia-pipeline-datos",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )
        state_machine = sfn.StateMachine(
            self,
            "PipelineDatos",
            state_machine_name="politeia-pipeline-datos",
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            timeout=Duration.minutes(15),
            logs=sfn.LogOptions(destination=sm_logs, level=sfn.LogLevel.ERROR),
        )

        CfnOutput(self, "PipelineArn", value=state_machine.state_machine_arn)
        CfnOutput(self, "AlertasTopicArn", value=topic.topic_arn,
                  description="Suscribir el email de alertas a este topic (a mano)")
        CfnOutput(self, "SourceKey", value=SOURCE_KEY,
                  description="Subí acá la vista_mapa base para disparar el pipeline")
        CfnOutput(self, "StagingKey", value=STAGING_KEY)
        CfnOutput(self, "LiveKey", value=LIVE_KEY)
