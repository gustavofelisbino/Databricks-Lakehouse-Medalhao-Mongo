# Arquitetura

## Fluxo de dados

```
[CSVs em data/raw/]
        │  Upload no Volume `workspace.landing.csv_raw` + notebook 00b
        ▼
[MongoDB Atlas: db `seguradora` (11 collections)]
        │  Notebook 01_landing_extracao_mongo (pymongo → JSONL)
        ▼
[Volume /Volumes/workspace/landing/dados/<col>.json]
        │  Notebook 02_bronze_ingestao (spark.read.json + auditoria)
        ▼
[workspace.bronze.* — 11 tabelas Delta managed]
        │  Notebook 03_silver_data_quality (renome + DQ + auditoria)
        ▼
[workspace.silver.* — 11 tabelas Delta managed]
        │  Notebook 04_gold_dimensional (MERGE dim + INSERT fato)
        ▼
[workspace.gold.* — dim_carro, dim_cliente, dim_localidade, dim_tempo, fato_sinistro]
```

## Decisões-chave

| # | Decisão | Motivo |
|---|---|---|
| 1 | Origem em MongoDB Atlas (não-relacional) | Cumpre o requisito do trabalho de "banco relacional ou não relacional" |
| 2 | Driver `pymongo` (driver-side) | Funciona em Serverless Compute do Free Edition; não exige Maven |
| 3 | Formato Landing: JSONL | `spark.read.json` lê nativamente sem `multiLine` |
| 4 | Delta managed em todas as camadas | Padrão do modelo do professor e do Free Edition |
| 5 | Catálogo `workspace` | Default do Free Edition |
| 6 | Schemas separados por camada | `landing`, `bronze`, `silver`, `gold` |
| 7 | Star schema com 4 dim + 1 fato | Espelha o notebook 004 do professor |
| 8 | SCD Type 1 via MERGE | Mesma técnica do professor |
| 9 | Job com 5 tasks sequenciais | Atende ao requisito "Jobs & Pipelines encadeado" |

## Camadas

| Camada | Schema | Formato | Conteúdo |
|---|---|---|---|
| Landing | volume `landing.dados` | JSONL | Dump bruto do Mongo |
| Bronze | `bronze` | Delta managed | + auditoria (`data_hora_bronze`, `nome_arquivo`) |
| Silver | `silver` | Delta managed | Renome (UPPER + expansão), trim, dedup, drop de `_id`/auditoria bronze, + auditoria silver |
| Gold | `gold` | Delta managed | Star schema Kimball |
