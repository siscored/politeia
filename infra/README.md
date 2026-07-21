# infra/ — Infraestructura como código (AWS CDK · Python)

IaC de POLITEIA. Toda la infra AWS se describe acá y se versiona con el repo.

## Config fija
| | |
|---|---|
| Cuenta AWS | `851679891137` (profile local `idetec`) |
| Región | `us-east-1` |
| Repo GitHub | `siscored/politeia` |
| Herramienta | AWS CDK v2 (Python) · CLI vía `npx aws-cdk` |

## Stacks
- **`PoliteiaGithubOidc`** — Provider OIDC de GitHub Actions + role de deploy
  (`politeia-github-deploy`) asumible solo desde este repo. Sin claves de larga
  vida. Es lo que conecta GitHub↔AWS.

> El bucket `electoral-data-851679891137` YA existe y se gestiona por fuera de
> CDK por ahora (versionado activado a mano). Adoptarlo con `cdk import` es un
> paso futuro; no recrearlo desde CDK para no arriesgar el dato.

## Bootstrap y primer deploy (una sola vez, local, con perfil admin)
```bash
# 1. entorno virtual (python a secas es el stub de MS Store; usar py)
py -m venv .venv
source .venv/Scripts/activate      # Git Bash en Windows
pip install -r requirements.txt

# 2. bootstrap de la cuenta (crea los roles cdk-hnb659fds-*)
npx aws-cdk@latest bootstrap aws://851679891137/us-east-1 --profile idetec

# 3. desplegar el stack OIDC
npx aws-cdk@latest deploy PoliteiaGithubOidc --profile idetec
```
El output `DeployRoleArn` se carga en GitHub como **variable de repo**
`AWS_DEPLOY_ROLE_ARN` (Settings → Secrets and variables → Actions → Variables).
Desde ahí, cada merge a `main` despliega solo (ver `.github/workflows/deploy.yml`).

## Comandos útiles
```bash
npx aws-cdk@latest synth --all       # genera CloudFormation, no despliega
npx aws-cdk@latest diff --profile idetec
npx aws-cdk@latest deploy --all --profile idetec
```
