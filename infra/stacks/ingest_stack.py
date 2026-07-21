"""
Run plane: Lambdas de ingesta que bajan datos a raw/.

Primera funcion: politeia-ingest-dine. Corre el codigo de ingest/dine/,
escribe SOLO en raw/dine/ y se puede disparar a mano o por horario
(EventBridge, arranca deshabilitado hasta tener el catalogo de URLs).
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_logs as logs,
)
from constructs import Construct


class IngestStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        data_bucket_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Grupo de logs propio (retencion 1 mes). Si no lo definimos, Lambda
        # crea uno que nunca expira; asi controlamos costo y nombre.
        log_group = logs.LogGroup(
            self,
            "IngestDineLogs",
            log_group_name="/aws/lambda/politeia-ingest-dine",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # La funcion Lambda.
        fn = lambda_.Function(
            self,
            "IngestDine",
            function_name="politeia-ingest-dine",
            runtime=lambda_.Runtime.PYTHON_3_12,     # runtime del contrato
            handler="handler.lambda_handler",         # archivo.funcion a invocar
            code=lambda_.Code.from_asset("../ingest/dine"),  # empaqueta esa carpeta
            timeout=Duration.minutes(5),              # corta si tarda mas
            memory_size=512,                          # MB (y CPU proporcional)
            log_group=log_group,
            environment={                             # variables de entorno
                "DATA_BUCKET": data_bucket_name,
                "RAW_PREFIX": "electoral/raw/dine",
            },
            description="Baja datos de DINE y los guarda crudos en raw/dine/ con linaje",
        )

        # Permisos minimos: escribir/leer SOLO en raw/dine/ (no en todo el bucket).
        fn.add_to_role_policy(
            iam.PolicyStatement(
                sid="EscribirRawDine",
                actions=["s3:PutObject", "s3:GetObject"],
                resources=[f"arn:aws:s3:::{data_bucket_name}/electoral/raw/dine/*"],
            )
        )

        # Disparador por horario. Arranca DESHABILITADO: se prende cuando haya
        # catalogo de URLs de DINE. Ejemplo: 1 vez por dia.
        rule = events.Rule(
            self,
            "IngestDineSchedule",
            rule_name="politeia-ingest-dine-schedule",
            schedule=events.Schedule.rate(Duration.days(1)),
            enabled=False,
            description="Dispara politeia-ingest-dine (deshabilitado por ahora)",
        )
        rule.add_target(targets.LambdaFunction(fn))

        CfnOutput(self, "FunctionName", value=fn.function_name)
        CfnOutput(self, "FunctionArn", value=fn.function_arn)
