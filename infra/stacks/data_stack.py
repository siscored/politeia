"""
Capa de datos consultable: catalogo Glue + Athena sobre los datos curados.

- Referencia (NO recrea) el bucket fuente de verdad electoral-data-*.
- Crea una base de datos Glue y un crawler que infiere el esquema de los
  CSV curados (consolidado, vista_mapa), cada uno en su subprefijo.
- Crea un workgroup de Athena con bucket propio para resultados.

Cuando se haga la migracion a Parquet particionado (HUECO #3), el crawler
apunta a los nuevos prefijos sin tocar el resto del stack.
"""
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_s3 as s3,
    aws_iam as iam,
    aws_glue as glue,
    aws_athena as athena,
)
from constructs import Construct


class DataStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        data_bucket_name: str,
        database_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Bucket fuente de verdad: ya existe, solo lo referenciamos.
        data_bucket = s3.Bucket.from_bucket_name(self, "DataBucket", data_bucket_name)

        # Bucket propio para resultados de consultas Athena (efimero).
        results_bucket = s3.Bucket(
            self,
            "AthenaResults",
            bucket_name=f"politeia-athena-results-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[s3.LifecycleRule(expiration=Duration.days(30))],
        )

        # Catalogo Glue (base de datos).
        database = glue.CfnDatabase(
            self,
            "GlueDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=database_name,
                description="Catalogo POLITEIA sobre datos curados (procesados/)",
            ),
        )

        # Role del crawler: Glue gestionado + lectura del bucket de datos.
        crawler_role = iam.Role(
            self,
            "CrawlerRole",
            role_name="politeia-glue-crawler-role",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                ),
            ],
        )
        data_bucket.grant_read(crawler_role)

        # Crawler: un target por dataset (cada uno en su subprefijo -> una tabla).
        base = f"s3://{data_bucket_name}/electoral/procesados"
        crawler = glue.CfnCrawler(
            self,
            "ProcesadosCrawler",
            name="politeia-crawler-procesados",
            role=crawler_role.role_arn,
            database_name=database_name,
            description="Infiere el esquema de consolidado y vista_mapa",
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(path=f"{base}/consolidado/"),
                    glue.CfnCrawler.S3TargetProperty(path=f"{base}/vista_mapa/"),
                ],
            ),
        )
        crawler.add_dependency(database)

        # Workgroup de Athena con salida en el bucket de resultados.
        athena.CfnWorkGroup(
            self,
            "Workgroup",
            name="politeia",
            recursive_delete_option=True,
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                enforce_work_group_configuration=True,
                publish_cloud_watch_metrics_enabled=True,
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    output_location=f"s3://{results_bucket.bucket_name}/athena/",
                    encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
                        encryption_option="SSE_S3",
                    ),
                ),
            ),
        )

        CfnOutput(self, "GlueDatabaseName", value=database_name)
        CfnOutput(self, "AthenaWorkgroup", value="politeia")
        CfnOutput(self, "AthenaResultsBucket", value=results_bucket.bucket_name)
        CfnOutput(self, "CrawlerName", value="politeia-crawler-procesados")
