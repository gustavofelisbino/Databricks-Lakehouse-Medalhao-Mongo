# Camada Silver

## Schema

`workspace.silver` — 11 tabelas Delta managed com Data Quality aplicado.

## Notebook

[`03_silver_data_quality.py`](../../notebooks/03_silver_data_quality.py)

## Regras de Data Quality

Para cada tabela `bronze.<t>`:

1. **Renome de colunas:** `UPPER` + expansão de prefixos/sufixos:

| De | Para |
|---|---|
| `CD_` | `CODIGO_` |
| `VL_` | `VALOR_` |
| `DT_` | `DATA_` |
| `NM_` | `NOME_` |
| `DS_` | `DESCRICAO_` |
| `NR_` | `NUMERO_` |
| `_UF` | `_UNIDADE_FEDERATIVA` |

2. **Drop de colunas obsoletas:**
   - `DATA_HORA_BRONZE`, `NOME_ARQUIVO` (auditoria bronze não é mais útil).
   - `_ID` (id Mongo, sem semântica no DW).

3. **Trim** em todas as colunas string.

4. **Dedup** (`dropDuplicates`) — proteção contra re-ingestão.

5. **Auditoria silver:**
   - `NOME_ARQUIVO_BRONZE` — `bronze.<t>` (rastreabilidade).
   - `DATA_ARQUIVO_SILVER` — `current_timestamp()`.

## Validação

```sql
SHOW TABLES IN silver;
SELECT * FROM silver.apolice LIMIT 5;   -- colunas em CAIXA_ALTA com prefixos expandidos
```
