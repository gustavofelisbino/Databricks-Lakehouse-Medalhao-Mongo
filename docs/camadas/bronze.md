# Camada Bronze

## Schema

`workspace.bronze` — 11 tabelas Delta managed.

## Notebook

[`02_bronze_ingestao.py`](../../notebooks/02_bronze_ingestao.py)

## Comportamento

Para cada JSONL em `landing.dados`:
1. `spark.read.json(path)` — inferência automática de schema.
2. Adiciona colunas de auditoria:
   - `data_hora_bronze` — `current_timestamp()`
   - `nome_arquivo` — `<col>.json`
3. `write.format("delta").mode("overwrite").saveAsTable("bronze.<col>")`.

## Validação

```sql
SHOW TABLES IN bronze;          -- 11 tabelas
DESCRIBE DETAIL bronze.apolice;  -- managed, location interno
SELECT COUNT(*) FROM bronze.apolice;
```
