# Databricks Lakehouse Medalhão — MongoDB

Pipeline de dados no **Databricks Free Edition** implementando a arquitetura Medallion (Landing → Bronze → Silver → Gold), com origem em **MongoDB Atlas** (não-relacional) e modelo dimensional Ralph Kimball no Gold. Todas as etapas orquestradas por **Jobs & Pipelines**.

> Trabalho 3 — Lakehouse com Databricks Free Edition e Arquitetura Medalhão.

## Arquitetura

```
[CSVs em data/raw/]
        │  Upload no Volume + 00b_seed_csv_para_mongo  (1x)
        ▼
[MongoDB Atlas — db `seguradora` (11 collections)]
        │  01_landing_extracao_mongo  (JSONL)
        ▼
[Volume workspace.landing.dados]
        │  02_bronze_ingestao  (+ auditoria)
        ▼
[workspace.bronze.* — 11 tabelas Delta]
        │  03_silver_data_quality  (renome + trim + dedup)
        ▼
[workspace.silver.* — 11 tabelas Delta]
        │  04_gold_dimensional  (MERGE dim + INSERT fato)
        ▼
[workspace.gold.* — 4 dim + 1 fato]
```

## Stack

- **Databricks Free Edition** (Serverless Compute, Unity Catalog, Volumes)
- **Delta Lake** (managed tables)
- **MongoDB Atlas M0** (origem não-relacional)
- **PyMongo** (driver de leitura)
- **MkDocs Material** (documentação)

## Estrutura

```
.
├── notebooks/                          # 7 notebooks Databricks (.py source)
│   ├── 00_setup_ambiente.py            # cria schemas + volumes
│   ├── 00b_seed_csv_para_mongo.py      # 1x: popula Atlas a partir dos CSVs
│   ├── 01_landing_extracao_mongo.py    # Mongo → JSONL no Volume
│   ├── 02_bronze_ingestao.py           # JSONL → Delta managed (bronze)
│   ├── 03_silver_data_quality.py       # DQ + renome + auditoria
│   ├── 04_gold_dimensional.py          # star schema Kimball
│   └── 99_destruir_ambiente.py         # limpeza (opcional)
├── data/raw/                           # 11 CSVs de origem
├── databricks_job.yml                  # Asset Bundle do Job
├── docs/                               # MkDocs
└── .github/workflows/mkdocs.yml        # deploy GitHub Pages
```

## Como rodar (tudo via Databricks)

Veja [`docs/runbook-databricks.md`](docs/runbook-databricks.md) para o passo-a-passo operacional completo. Resumo:

1. **Pré-requisitos:** conta no Databricks Free Edition + cluster M0 no MongoDB Atlas (com Network Access liberado em `0.0.0.0/0` e usuário criado).
2. **Conectar Git Folder** no Databricks → este repositório.
3. **Configurar credencial Mongo** — Secret Scope `mongo` (key `uri`) via Databricks CLI, ou Job Parameter `MONGODB_URI` como fallback.
4. **Rodar manualmente:**
   - `00_setup_ambiente` (cria schemas + volumes)
   - Upload dos 11 CSVs em `data/raw/` → Catalog Explorer → volume `workspace.landing.csv_raw` (drag-and-drop)
   - `00b_seed_csv_para_mongo` (popula Atlas)
5. **Criar Job** `pipeline_seguradora_medalhao` com 5 tasks sequenciais (`setup → landing → bronze → silver → gold`).
6. **Run now** → conferir DAG verde.

## Modelo Dimensional (Gold)

| Tabela | Tipo | Chave/Negócio |
|---|---|---|
| `gold.dim_carro` | Dimensão | PLACA |
| `gold.dim_cliente` | Dimensão | CODIGO_CLIENTE |
| `gold.dim_localidade` | Dimensão | CODIGO_MUNICIPIO |
| `gold.dim_tempo` | Dimensão | Data (range 2023-01-01 → 2026-12-31) |
| `gold.fato_sinistro` | Fato | FK_TEMPO + FK_LOCALIDADE + FK_CARRO + FK_CLIENTE |

Carga das dimensões: **SCD Type 1** via `MERGE INTO`. Fato carregada com agregação `COUNT(1)` por dia/local/carro/cliente.

## Documentação completa

- [Arquitetura](docs/arquitetura.md)
- Camadas: [Landing](docs/camadas/landing.md) · [Bronze](docs/camadas/bronze.md) · [Silver](docs/camadas/silver.md) · [Gold](docs/camadas/gold.md)
- [Modelo Dimensional](docs/modelo-dimensional.md)
- [Job & Pipeline](docs/job-pipeline.md)
- [Setup MongoDB](docs/setup-mongo.md)
- [Runbook Databricks](docs/runbook-databricks.md)

## Autor

Gustavo Dias — Trabalho 3 — 2026-05-12.
