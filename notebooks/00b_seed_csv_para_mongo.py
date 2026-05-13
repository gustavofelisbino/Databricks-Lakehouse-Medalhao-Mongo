# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # 00b — Carga inicial CSV → MongoDB Atlas
# MAGIC
# MAGIC Lê os 11 CSVs do volume `workspace.landing.csv_raw` (upload manual)
# MAGIC e popula o banco `seguradora` no Atlas. Roda **uma vez**, fora do Job.
# MAGIC Idempotente: drop + insert.

# COMMAND ----------
# MAGIC %pip install pymongo pandas

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
# Credencial via Secret Scope (preferido); fallback para widget
try:
    MONGO_URI = dbutils.secrets.get(scope="mongo", key="uri")
except Exception:
    dbutils.widgets.text("MONGODB_URI", "")
    MONGO_URI = dbutils.widgets.get("MONGODB_URI")

assert MONGO_URI, "MONGODB_URI não configurado (secret scope 'mongo'/'uri' ou widget)"

# COMMAND ----------
import pandas as pd
from pymongo import MongoClient

CSV_PATH = "/Volumes/workspace/landing/csv_raw"
DATABASE = "seguradora"
TABELAS = [
    "apolice", "carro", "cliente", "endereco", "estado", "marca",
    "modelo", "municipio", "regiao", "sinistro", "telefone",
]

client = MongoClient(MONGO_URI)
db = client[DATABASE]

for t in TABELAS:
    df = pd.read_csv(f"{CSV_PATH}/{t}.csv", dtype=str, keep_default_na=False)
    docs = df.to_dict(orient="records")
    db[t].drop()
    if docs:
        db[t].insert_many(docs)
    print(f"{t}: {len(docs)} docs inseridos")

client.close()
print("Seed concluído.")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Validação
# MAGIC Abra Atlas → Browse Collections → confirme banco `seguradora` com 11 collections populadas.
