# Runbook Databricks — operação ponta-a-ponta

Tudo é feito na UI do Databricks Free Edition + Atlas (web). Sem Python local.

## Pré-requisitos

- Conta no Databricks Free Edition (Serverless habilitado).
- Cluster M0 no MongoDB Atlas configurado conforme [Setup MongoDB](setup-mongo.md), com connection string em mãos.

## Passo 1 — Conectar o repositório no Databricks

1. **Workspace** → botão **Add** → **Git folder**.
2. URL: `https://github.com/<seu-usuario>/Databricks-Lakehouse-Medalhao-Mongo` · Provider: GitHub · Branch: `main`.
3. **Create**. O clone aparecerá em `/Workspace/Users/<seu-email>/Databricks-Lakehouse-Medalhao-Mongo`.

## Passo 2 — Configurar credencial Mongo

### Opção A — Secret Scope (recomendado)

Em um terminal com Databricks CLI instalado:

```bash
pip install databricks-cli
databricks auth login --host https://<seu-workspace>.cloud.databricks.com
databricks secrets create-scope mongo
databricks secrets put-secret mongo uri
# (cole a connection string quando solicitado)
```

### Opção B — Job Parameter (fallback, 100% UI)

Pula o secret scope. A string será passada como parâmetro do Job (Passo 5). O notebook lê automaticamente do widget se o secret não existir.

## Passo 3 — Setup e seed (uma vez)

1. Abrir e **Run** `notebooks/00_setup_ambiente.py`.
   - Verificar output: 4 schemas + 2 volumes em `workspace`.
2. **Catalog Explorer** → `workspace` → `landing` → volume `csv_raw` → botão **Upload to this volume** → selecionar os 11 CSVs de `data/raw/`.
3. Abrir e **Run** `notebooks/00b_seed_csv_para_mongo.py`.
   - Output esperado: 11 linhas `<col>: N docs inseridos`.
4. Conferir no Atlas: **Browse Collections** → banco `seguradora` com 11 collections.

## Passo 4 — Sanity check da extração

Antes de criar o Job, validar manualmente:

- Abrir e **Run** `notebooks/01_landing_extracao_mongo.py`.
- Output: 11 linhas `<col>: N docs → /Volumes/.../<col>.json`.
- Última célula: `dbutils.fs.ls` deve mostrar 11 arquivos `.json`.

Se falhar, problema na credencial ou network do Atlas.

## Passo 5 — Criar o Job

UI → **Jobs & Pipelines** → **Create Job** → nome `pipeline_seguradora_medalhao`.

Adicionar **5 tasks** sequenciais:

| # | Task name | Type | Notebook path (do Git Folder) | Depends on |
|---|---|---|---|---|
| 1 | `setup` | Notebook | `notebooks/00_setup_ambiente` | (none) |
| 2 | `landing` | Notebook | `notebooks/01_landing_extracao_mongo` | `setup` |
| 3 | `bronze` | Notebook | `notebooks/02_bronze_ingestao` | `landing` |
| 4 | `silver` | Notebook | `notebooks/03_silver_data_quality` | `bronze` |
| 5 | `gold` | Notebook | `notebooks/04_gold_dimensional` | `silver` |

- **Compute**: Serverless em todas.
- **Max retries**: 1 em cada.
- Se usar **Opção B** do Passo 2: adicionar Job Parameter `MONGODB_URI = mongodb+srv://...`.

Salvar.

## Passo 6 — Run

- Botão **Run now** no topo do Job.
- Acompanhar o DAG: cada bolinha verde = task ok.
- Tempo total esperado: 3–8 min (depende do cold start do Serverless).

## Passo 7 — Validação

Em qualquer notebook ou SQL editor:

```sql
SHOW SCHEMAS IN workspace;                          -- landing, bronze, silver, gold
SHOW TABLES IN bronze;                              -- 11 tabelas
SHOW TABLES IN silver;                              -- 11 tabelas
SHOW TABLES IN gold;                                -- 5 tabelas (4 dim + 1 fato)

SELECT COUNT(*) FROM gold.fato_sinistro;            -- > 0
SELECT * FROM silver.apolice LIMIT 5;               -- colunas em CAIXA_ALTA
SELECT COUNT(*) FROM gold.dim_tempo;                -- ~1461 dias (4 anos)
```

## Passo 8 — Entrega no GitHub

- Push do branch `main` no GitHub.
- Confirmar deploy do MkDocs em GitHub Pages (Actions → workflow `Deploy MkDocs` verde).
- (Opcional) printar o DAG verde do Job e colocar no README ou docs.

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `pymongo.errors.ServerSelectionTimeoutError` | Network Access do Atlas não liberado | Voltar ao Setup MongoDB, liberar `0.0.0.0/0` |
| `AssertionError: MONGODB_URI não configurado` | Secret + widget ambos ausentes | Configurar Secret Scope OU passar Job Parameter |
| `Authentication failed` | Senha incorreta ou URL-encoding necessário | Verificar usuário/senha; se senha tem `@:/?#`, URL-encodar ou trocar |
| Task `gold` falha com `column not found` | Nome de coluna do silver não bate com SQL | Inspecionar `silver.sinistro` (e outras), ajustar nomes no notebook 04 |
| Job lento | Cold start do Serverless | Normal na 1ª run; subsequentes são mais rápidas |
