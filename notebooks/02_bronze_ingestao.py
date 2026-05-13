# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # 02 — Bronze (JSONL → Delta managed em `workspace.bronze.*`)
# MAGIC
# MAGIC Lê cada arquivo JSONL do volume `landing.dados`, adiciona auditoria
# MAGIC (`data_hora_bronze`, `nome_arquivo`) e grava como Delta managed.

# COMMAND ----------
from pyspark.sql.functions import current_timestamp, lit

LANDING = "/Volumes/workspace/landing/dados"
TABELAS = [
    "apolice", "carro", "cliente", "endereco", "estado", "marca",
    "modelo", "municipio", "regiao", "sinistro", "telefone",
]

for t in TABELAS:
    df = (
        spark.read.json(f"{LANDING}/{t}.json")
        .withColumn("data_hora_bronze", current_timestamp())
        .withColumn("nome_arquivo", lit(f"{t}.json"))
    )
    (df.write.format("delta").mode("overwrite").saveAsTable(f"bronze.{t}"))
    print(f"bronze.{t} ok ({df.count()} linhas)")

# COMMAND ----------
# MAGIC %sql SHOW TABLES IN bronze;

# COMMAND ----------
# MAGIC %sql DESCRIBE DETAIL bronze.apolice;
