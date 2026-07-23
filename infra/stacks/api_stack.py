"""
API read-only del mapa electoral.

Lambda politeia-api-mapa detrás de un API Gateway HTTP API (v2). Lee
vista_mapa desde S3. Es el endpoint que consume el frontend "Comando IA".

Por qué HTTP API (v2) y no REST (v1):
  - El handler ya usa el payload v2 (requestContext.http.method) → no cambia.
  - Más barato y de menor latencia; suficiente para un read-only público.
  - Throttling a nivel stage (rate/burst) pone el techo de costo que la
    Function URL no tenía (auth NONE, sin límite → un curl en loop escalaba).

Por qué NO configuramos CORS en el API Gateway:
  - El CORS lo setea el handler (un solo Access-Control-Allow-Origin). Si además
    lo activáramos acá, el proxy agregaría un segundo header y el browser
    rechazaría el fetch por duplicado (mismo bug que la Function URL echoando el
    Origin — ver DECISIONES.md 2026-07-21). Una sola fuente de CORS: el handler.
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_int,
)
from constructs import Construct

# Techo de abuso del endpoint público. Una consola de campaña con pocos usuarios
# está muy por debajo de esto; el objetivo es cortar un loop malicioso, no
# limitar el uso legítimo. Subir si hiciera falta.
THROTTLE_RATE = 20    # req/seg sostenidas
THROTTLE_BURST = 40   # ráfaga instantánea


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        data_bucket_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        log_group = logs.LogGroup(
            self,
            "ApiMapaLogs",
            log_group_name="/aws/lambda/politeia-api-mapa",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        fn = lambda_.Function(
            self,
            "ApiMapa",
            function_name="politeia-api-mapa",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../api/mapa"),
            timeout=Duration.seconds(30),
            memory_size=512,
            log_group=log_group,
            environment={
                "DATA_BUCKET": data_bucket_name,
                "VISTA_MAPA_KEY": "electoral/procesados/vista_mapa/vista_mapa.csv",
            },
            description="API read-only del mapa: vista_mapa filtrado por distrito/año/cargo",
        )

        # Solo lectura de los curados (vista_mapa + geo).
        fn.add_to_role_policy(
            iam.PolicyStatement(
                sid="LeerCurados",
                actions=["s3:GetObject"],
                resources=[f"arn:aws:s3:::{data_bucket_name}/electoral/procesados/*"],
            )
        )

        # --- API Gateway HTTP API (v2) --------------------------------------
        # Integración proxy: el API GW pasa el request al handler tal cual y
        # devuelve su respuesta sin tocarla (por eso el CORS del handler llega
        # intacto). La ruta ANY / cubre GET (datos) y OPTIONS (preflight, que el
        # handler responde con 204). El front siempre pega a "/" con querystring.
        integration = apigwv2_int.HttpLambdaIntegration("ApiMapaIntegration", fn)

        http_api = apigwv2.HttpApi(
            self,
            "ApiMapaHttp",
            api_name="politeia-api-mapa",
            description="API read-only del mapa electoral (HTTP API v2, proxy a Lambda)",
        )
        http_api.add_routes(
            path="/",
            methods=[apigwv2.HttpMethod.ANY],
            integration=integration,
        )

        # Throttling en el stage por defecto ($default). El L2 no expone el
        # throttle directo: bajamos al CfnStage y le seteamos las route settings.
        default_stage = http_api.default_stage.node.default_child  # CfnStage
        default_stage.default_route_settings = apigwv2.CfnStage.RouteSettingsProperty(
            throttling_rate_limit=THROTTLE_RATE,
            throttling_burst_limit=THROTTLE_BURST,
        )

        # Mismo OutputKey que antes (ApiMapaUrl): deploy.yml lo lee para inyectar
        # VITE_API_URL en el build del front. El endpoint cambia de dominio
        # (lambda-url → execute-api) pero el contrato del output no.
        CfnOutput(self, "ApiMapaUrl", value=http_api.url, description="URL del API del mapa (API Gateway HTTP)")
