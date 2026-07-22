"""
Confianza OIDC entre GitHub Actions y AWS.

Crea:
  1. El Identity Provider OIDC de GitHub (uno por cuenta).
  2. Un role de deploy asumible SOLO desde el repo siscored/politeia,
     sin claves de larga vida guardadas en GitHub Secrets.

El role no lleva permisos amplios: solo puede asumir los roles que crea
`cdk bootstrap` (qualifier hnb659fds). Asi el deploy real corre con los
permisos acotados de CDK, no con un role CI todopoderoso.
"""
from aws_cdk import Stack, CfnOutput, Duration
from aws_cdk import aws_iam as iam
from constructs import Construct


class GithubOidcStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        github_subjects: list,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Provider OIDC de GitHub Actions.
        provider = iam.OpenIdConnectProvider(
            self,
            "GithubOidcProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
        )

        # Alcance del trust: los 'sub' permitidos (ver app.py). Se aceptan el
        # formato estandar y el custom con IDs numericos que usa la org siscored.
        # Endurecer a ":ref:refs/heads/main" cuando quieras limitar solo a main.
        subject = github_subjects

        # 2. Role asumido por GitHub Actions via el token OIDC.
        deploy_role = iam.Role(
            self,
            "GithubDeployRole",
            role_name="politeia-github-deploy",
            description="Asumido por GitHub Actions (OIDC) para desplegar POLITEIA via CDK",
            max_session_duration=Duration.hours(1),
            assumed_by=iam.WebIdentityPrincipal(
                provider.open_id_connect_provider_arn,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": subject,
                    },
                },
            ),
        )

        # 3a. Asumir los roles de CDK bootstrap (deploy de infra acotado).
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="AssumeCdkBootstrapRoles",
                actions=["sts:AssumeRole"],
                resources=[
                    f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-*"
                ],
            )
        )

        # 3c. Leer el dataset curado para validarlo en el CI (gate de datos).
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="LeerDatasetCurado",
                actions=["s3:GetObject"],
                resources=[
                    "arn:aws:s3:::electoral-data-851679891137/electoral/procesados/*"
                ],
            )
        )

        # 3b. Desplegar el frontend a Amplify (manual deployment desde el CI).
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="DesplegarFrontendAmplify",
                actions=[
                    "amplify:CreateDeployment",
                    "amplify:StartDeployment",
                    "amplify:GetJob",
                    "amplify:GetApp",
                    "amplify:GetBranch",
                    "cloudformation:DescribeStacks",
                ],
                resources=["*"],
            )
        )

        CfnOutput(
            self,
            "DeployRoleArn",
            value=deploy_role.role_arn,
            description="Cargar como variable AWS_DEPLOY_ROLE_ARN en el repo de GitHub",
        )
        CfnOutput(
            self,
            "OidcProviderArn",
            value=provider.open_id_connect_provider_arn,
        )
