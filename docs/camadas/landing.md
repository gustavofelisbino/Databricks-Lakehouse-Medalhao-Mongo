# Camada Landing

## Volume

- `workspace.landing.dados` — output da extração (JSONL).
- `workspace.landing.csv_raw` — input do seed (CSVs originais, upload manual).

## Notebook

[`01_landing_extracao_mongo.py`](../../notebooks/01_landing_extracao_mongo.py)

## Comportamento

- Lê `MONGODB_URI` via Secret Scope (`scope=mongo`, `key=uri`) ou widget (fallback).
- Conecta no banco `seguradora` no Atlas.
- Para cada uma das 11 collections, lê todos os documentos via `db[col].find({})`.
- Converte `_id` ObjectId para string (JSON-serializável).
- Grava 1 arquivo JSONL por collection (`<col>.json`, 1 doc por linha).

## Saída esperada

```
/Volumes/workspace/landing/dados/
  apolice.json
  carro.json
  cliente.json
  endereco.json
  estado.json
  marca.json
  modelo.json
  municipio.json
  regiao.json
  sinistro.json
  telefone.json
```

## Validação

```sql
-- Listar arquivos
LIST '/Volumes/workspace/landing/dados/';
```

Ou no notebook: `display(dbutils.fs.ls('/Volumes/workspace/landing/dados'))`
