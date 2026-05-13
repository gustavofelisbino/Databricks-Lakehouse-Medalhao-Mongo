# Camada Gold

## Schema

`workspace.gold` — 4 dimensões + 1 fato (star schema Ralph Kimball).

## Notebook

[`04_gold_dimensional.py`](../../notebooks/04_gold_dimensional.py)

## Tabelas

Ver [Modelo Dimensional](../modelo-dimensional.md) para o detalhe de colunas.

## Estratégias de carga

- **Dimensões `dim_carro`, `dim_cliente`, `dim_localidade`:** `MERGE INTO` com SCD Type 1. JOINs originados das tabelas silver.
- **`dim_tempo`:** gerada via `spark.range` para o intervalo 2023-01-01 → 2026-12-31.
- **`fato_sinistro`:** `TRUNCATE TABLE` + `INSERT INTO ... SELECT` com `COUNT(1)` agrupado por `(data, sk_localidade, sk_carro, sk_cliente)`. Carga full reload (pequeno volume).

## Validação

```sql
SHOW TABLES IN gold;                              -- 5 tabelas

SELECT COUNT(*) AS total FROM gold.fato_sinistro; -- > 0
SELECT COUNT(*) FROM gold.dim_carro;
SELECT COUNT(*) FROM gold.dim_cliente;
SELECT COUNT(*) FROM gold.dim_localidade;
SELECT COUNT(*) FROM gold.dim_tempo;              -- ~1461 (4 anos)

-- Sample de análise
SELECT t.Ano,
       l.NOME_ESTADO,
       SUM(f.QTDE_SINISTRO) AS total_sinistros
FROM gold.fato_sinistro f
INNER JOIN gold.dim_tempo      t ON f.FK_TEMPO     = t.Data
INNER JOIN gold.dim_localidade l ON f.FK_LOCALIDADE = l.SK_LOCALIDADE
GROUP BY t.Ano, l.NOME_ESTADO
ORDER BY total_sinistros DESC;
```
