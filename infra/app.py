#!/usr/bin/env python3
"""
POLITEIA — punto de entrada de la infraestructura como código (AWS CDK).

Config central del despliegue. La cuenta y region estan fijadas al bucket
fuente de verdad (ver CLAUDE.md §0 y docs/06_estado_bucket.md).
"""
import aws_cdk as cdk

from stacks.github_oidc_stack import GithubOidcStack
from stacks.data_stack import DataStack
from stacks.ingest_stack import IngestStack
from stacks.pipeline_stack import PipelineStack
from stacks.api_stack import ApiStack
from stacks.web_stack import WebStack

# --- Config del proyecto (unica fuente de verdad para la infra) ---
ACCOUNT = "851679891137"          # cuenta donde vive el dato (profile idetec)
REGION = "us-east-1"
DATA_BUCKET = "electoral-data-851679891137"   # bucket fuente de verdad (ya existe)
GLUE_DATABASE = "politeia_electoral"          # catalogo Athena (guiones no permitidos)
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

# Rótulo de control: todo recurso soportado queda etiquetado Project=politeia
# (agrupa/identifica costos e inventario en la consola). Complementa el prefijo
# de naming politeia-* que llevan los nombres de los recursos.
cdk.Tags.of(app).add("Project", "politeia")

# Stack 1: confianza OIDC GitHub Actions -> AWS + role de deploy.
# Se despliega UNA vez a mano (admin), despues GitHub Actions se encarga.
GithubOidcStack(
    app,
    "PoliteiaGithubOidc",
    github_subjects=github_subjects,
    env=env,
    description="OIDC GitHub Actions + deploy role para POLITEIA",
)

# Stack 2: capa de datos consultable (Glue + Athena) sobre lo curado.
DataStack(
    app,
    "PoliteiaData",
    data_bucket_name=DATA_BUCKET,
    database_name=GLUE_DATABASE,
    env=env,
    description="Catalogo Glue + Athena sobre datos curados de POLITEIA",
)

# Stack 3: run plane — Lambdas de ingesta (empiezan con DINE).
IngestStack(
    app,
    "PoliteiaIngest",
    data_bucket_name=DATA_BUCKET,
    env=env,
    description="Lambdas de ingesta de POLITEIA (raw/)",
)

# Stack 3b: pipeline de datos (normaliza→valida→publica) con gate en _staging.
PipelineStack(
    app,
    "PoliteiaPipeline",
    data_bucket_name=DATA_BUCKET,
    env=env,
    description="Pipeline reproducible de vista_mapa (Step Functions + Lambdas) de POLITEIA",
)

# Stack 4: API read-only del mapa (lo consume el frontend).
ApiStack(
    app,
    "PoliteiaApi",
    data_bucket_name=DATA_BUCKET,
    env=env,
    description="API read-only del mapa electoral de POLITEIA",
)

# Stack 5: hosting del frontend en Amplify.
WebStack(
    app,
    "PoliteiaWeb",
    env=env,
    description="Hosting Amplify del frontend Comando IA",
)

app.synth()
