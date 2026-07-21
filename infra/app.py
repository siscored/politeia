#!/usr/bin/env python3
"""
POLITEIA — punto de entrada de la infraestructura como código (AWS CDK).

Config central del despliegue. La cuenta y region estan fijadas al bucket
fuente de verdad (ver CLAUDE.md §0 y docs/06_estado_bucket.md).
"""
import aws_cdk as cdk

from stacks.github_oidc_stack import GithubOidcStack

# --- Config del proyecto (unica fuente de verdad para la infra) ---
ACCOUNT = "851679891137"          # cuenta donde vive el dato (profile idetec)
REGION = "us-east-1"
GITHUB_OWNER = "siscored"
GITHUB_REPO = "politeia"

app = cdk.App()
env = cdk.Environment(account=ACCOUNT, region=REGION)

# Stack 1: confianza OIDC GitHub Actions -> AWS + role de deploy.
# Se despliega UNA vez a mano (admin), despues GitHub Actions se encarga.
GithubOidcStack(
    app,
    "PoliteiaGithubOidc",
    github_owner=GITHUB_OWNER,
    github_repo=GITHUB_REPO,
    env=env,
    description="OIDC GitHub Actions + deploy role para POLITEIA",
)

app.synth()
