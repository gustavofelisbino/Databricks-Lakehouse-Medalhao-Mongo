# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # 01 — Extração MongoDB → Landing (JSONL no Volume)
# MAGIC
# MAGIC Lê todas as 11 collections do banco `seguradora` no Atlas e grava
# MAGIC um arquivo JSONL por collection em `/Volumes/workspace/landing/dados/`.

# COMMAND ----------
# MAGIC %pip install pymongo

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
try:
    MONGO_URI = dbutils.secrets.get(scope="mongo", key="uri")
except Exception:
    dbutils.widgets.text("MONGODB_URI", "")
    MONGO_URI = dbutils.widgets.get("MONGODB_URI")

assert MONGO_URI, "MONGODB_URI não configurado"

# COMMAND ----------
import json
from pymongo import MongoClient

DATABASE = "seguradora"
LANDING_PATH = "/Volumes/workspace/landing/dados"
COLECOES = [
    "apolice", "carro", "cliente", "endereco", "estado", "marca",
    "modelo", "municipio", "regiao", "sinistro", "telefone",
]

client = MongoClient(MONGO_URI)
db = client[DATABASE]

for col in COLECOES:
    docs = list(db[col].find({}))
    for d in docs:
        d["_id"] = str(d["_id"])
    destino = f"{LANDING_PATH}/{col}.json"
    with open(destino, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False, default=str) + "\n")
    print(f"{col}: {len(docs)} docs → {destino}")

client.close()

# COMMAND ----------
display(dbutils.fs.ls(LANDING_PATH))
