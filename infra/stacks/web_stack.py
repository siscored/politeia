"""
Hosting del frontend en AWS Amplify.

Crea la app Amplify `politeia-web` + branch `main`. NO se conecta al repo de
GitHub (evita manejar un token de GitHub): el contenido se despliega por
'manual deployment' desde el pipeline (ver .github/workflows/deploy.yml), que
buildea web/ y sube el artefacto. Así todo el deploy pasa por el OIDC que ya
tenemos, sin secretos nuevos.
"""
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_amplify as amplify,
)
from constructs import Construct


class WebStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app = amplify.CfnApp(
            self,
            "WebApp",
            name="politeia-web",
            platform="WEB",
            # SPA: cualquier ruta no encontrada cae en index.html.
            custom_rules=[
                amplify.CfnApp.CustomRuleProperty(source="/<*>", target="/index.html", status="404-200"),
            ],
        )
        amplify.CfnBranch(self, "Main", app_id=app.attr_app_id, branch_name="main", stage="PRODUCTION")

        CfnOutput(self, "AmplifyAppId", value=app.attr_app_id)
        CfnOutput(self, "WebUrl", value="https://main." + app.attr_default_domain, description="URL pública del frontend")
