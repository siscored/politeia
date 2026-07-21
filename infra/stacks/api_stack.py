"""
API read-only del mapa electoral.

Lambda politeia-api-mapa detrás de una Function URL (pública, CORS abierto —
los datos son públicos). Lee vista_mapa desde S3. Es el endpoint que consume
el frontend "Comando IA".
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct


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

        # Function URL pública con CORS (los datos electorales son públicos).
        url = fn.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
            cors=lambda_.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[lambda_.HttpMethod.GET],
            ),
        )

        CfnOutput(self, "ApiMapaUrl", value=url.url, description="URL del API del mapa")
