# POLITEIA MVP — CLAUDE.md (repo de la app)

> Claude Code lee este archivo al inicio de cada sesión (PC de Federico y de Esteban).
> El contrato de DATOS vive aparte (repo politeia + proyecto madre "POLITEIA · Auditor"
> en claude.ai, que emite las órdenes de trabajo OT-NNN).

## Qué es esto

- MVP de POLITEIA ("Comando IA"), inteligencia electoral para Argentina.
- Este MVP deploya en: https://main.d3w3982cnzzi0m.amplifyapp.com/
- Objetivo visual/funcional (mockup, NO TOCAR): https://main.d1pthxba9jy105.amplifyapp.com/
- Backend real: API Gateway + Lambda. Sin Cognito por ahora (demo a cliente). No agregar auth sin OT.

## Topología AWS — LEER ANTES DE CUALQUIER COMANDO aws

| Recurso | Profile | Región | Cuenta |
|---|---|---|---|
| MVP (esta app: Amplify, Lambda, API GW) | `personal` | `sa-east-1` | (ver `sts get-caller-identity`) |
| Mockup + bucket de datos | `fsc` | `us-east-1` | 851679891137 |

- **SIEMPRE** pasar `--profile` y `--region` explícitos. Nunca usar el default.
- El MVP quedó en São Paulo por accidente; migrar a us-east-1 es una OT futura. No crear recursos nuevos sin confirmar región.
- Bucket `s3://electoral-data-851679891137/electoral/` (profile `fsc`): **SOLO lectura**. `procesados/vista_mapa.csv` es el contrato del mapa.
- El mockup y la cuenta fsc son solo-lectura siempre, salvo OT explícita.

## Regla nº1: nunca trabajar sin orden de trabajo

Toda tarea llega como OT-NNN del proyecto madre (define branch, alcance, cuenta AWS y criterios). Pedido sin OT = borrador no mergeable; sugerir generar la OT.

## Flujo git (Fede + Esteban — NO negociable)

1. `git checkout main && git pull origin main` al inicio de CADA sesión.
2. Branch por OT con prefijo de persona: `fede/ot-012-...`, `este/ot-013-...`. Nunca commitear a main. Las branches mueren al mergear; no reutilizar.
3. Commits chicos, en español: `OT-012: agrega filtro por circuito`.
4. Al terminar: push + PR a main. El resumen del PR (qué, archivos, validación, pendientes) se pega en el proyecto madre para auditoría.
5. Merge SOLO con veredicto APROBADO del auditor. Merge = deploy automático.
6. Conflictos con trabajo del otro: resolver, rebuild, explicarlo en el PR.

## Definición de Terminado (por PR)

- [ ] Todos los criterios de aceptación de la OT.
- [ ] `npm run build` sin errores ni warnings nuevos; lint/typecheck si existen.
- [ ] Si tocó datos: `core/validadores.py` corrido y output en el resumen del PR.
- [ ] Sin secretos, sin PII, sin credenciales en código ni logs commiteados.
- [ ] Nada tocado fuera del alcance de la OT.
- [ ] Profile/región correctos en todo comando aws ejecutado.

## Convenciones

- Respetar el stack existente; no sumar frameworks/libs sin OT que lo apruebe.
- Textos de UI en español (Argentina).
- Nombres de campos = esquema real (docs/02 del repo politeia). No inventar columnas ni hardcodear datos que ya sirve el backend.
- Agrupaciones políticas: el mapeo histórico vive en `core/agrupaciones/` (repo politeia). Nunca mapear siglas a mano en el front.
- DINE (provisorio) vs Junta (definitivo): brecha 0,4–7% esperable, no es bug. Todo número mostrado debe rastrearse a su fuente.
- Circuitos pre/post 2019 se comparan vía `circuito_padre`.

## Comandos frecuentes

```bash
git checkout main && git pull origin main
aws sts get-caller-identity --profile personal
aws sts get-caller-identity --profile fsc
aws amplify list-apps --profile personal --region sa-east-1
aws s3 ls s3://electoral-data-851679891137/electoral/procesados/ --profile fsc
npm run build && npm run lint
```
