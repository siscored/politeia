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
        github_owner: str,
        github_repo: str,
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

        # Alcance del trust: cualquier ref del repo (branches, PRs, tags).
        # Endurecer a "repo:owner/repo:ref:refs/heads/main" cuando quieras
        # limitar el deploy solo a main.
        subject = f"repo:{github_owner}/{github_repo}:*"

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

        # 3. Unico permiso: asumir los roles de CDK bootstrap (deploy acotado).
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="AssumeCdkBootstrapRoles",
                actions=["sts:AssumeRole"],
                resources=[
                    f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-*"
                ],
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
