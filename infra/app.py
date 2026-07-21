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
# La org siscored personaliza el claim OIDC e inyecta los IDs numericos
# inmutables en el 'sub' (repo:owner@ownerid/repo@repoid:...). Aceptamos
# ambos formatos: el estandar y el custom con IDs. Ver CLAUDE.md / CloudTrail.
GITHUB_OWNER_ID = "266059589"
GITHUB_REPO_ID = "1305266911"

github_subjects = [
    f"repo:{GITHUB_OWNER}/{GITHUB_REPO}:*",
    f"repo:{GITHUB_OWNER}@{GITHUB_OWNER_ID}/{GITHUB_REPO}@{GITHUB_REPO_ID}:*",
]

app = cdk.App()
env = cdk.Environment(account=ACCOUNT, region=REGION)

# Stack 1: confianza OIDC GitHub Actions -> AWS + role de deploy.
# Se despliega UNA vez a mano (admin), despues GitHub Actions se encarga.
GithubOidcStack(
    app,
    "PoliteiaGithubOidc",
    github_subjects=github_subjects,
    env=env,
    description="OIDC GitHub Actions + deploy role para POLITEIA",
)

app.synth()
