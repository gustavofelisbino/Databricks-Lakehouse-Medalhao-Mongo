# Lakehouse Medalhão com Databricks Free Edition

Documentação técnica do Trabalho 3 — Lakehouse com arquitetura Medallion (Landing → Bronze → Silver → Gold) implementada no Databricks Free Edition, com origem em MongoDB Atlas.

## Visão geral

- **Origem:** MongoDB Atlas (não-relacional) com 11 collections do domínio de seguros de automóvel.
- **Plataforma:** Databricks Free Edition (Serverless Compute, Unity Catalog, Volumes, Delta Lake).
- **Orquestração:** 1 Job no Databricks com 5 tasks sequenciais.
- **Modelagem analítica:** Star schema Ralph Kimball com 4 dimensões e 1 tabela fato.

## Navegação

- **[Arquitetura](arquitetura.md)** — diagrama medallion e decisões.
- **Camadas:** [Landing](camadas/landing.md) · [Bronze](camadas/bronze.md) · [Silver](camadas/silver.md) · [Gold](camadas/gold.md).
- **[Modelo Dimensional](modelo-dimensional.md)** — descrição das dimensões e fato.
- **[Job & Pipeline](job-pipeline.md)** — DAG e YAML do Asset Bundle.
- **[Setup MongoDB](setup-mongo.md)** — passo-a-passo Atlas.
- **[Runbook Databricks](runbook-databricks.md)** — operação ponta-a-ponta na UI.
