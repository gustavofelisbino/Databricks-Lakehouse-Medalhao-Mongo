# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # 03 — Silver (Data Quality + padronização de nomes)
# MAGIC
# MAGIC Regras aplicadas em cada tabela bronze:
# MAGIC - Renome de colunas: UPPER + expansão dos prefixos `CD_/VL_/DT_/NM_/DS_/NR_/_UF`
# MAGIC - Drop de colunas obsoletas: `DATA_HORA_BRONZE`, `NOME_ARQUIVO`, `_ID`
# MAGIC - `trim` em todas colunas string
# MAGIC - `dropDuplicates` (proteção contra re-ingestão)
# MAGIC - Auditoria: `NOME_ARQUIVO_BRONZE`, `DATA_ARQUIVO_SILVER`
# MAGIC - Saída: `silver.*` como Delta managed (overwrite)

# COMMAND ----------
from pyspark.sql import functions as F

REGRAS = [
    ("CD_", "CODIGO_"),
    ("VL_", "VALOR_"),
    ("DT_", "DATA_"),
    ("NM_", "NOME_"),
    ("DS_", "DESCRICAO_"),
    ("NR_", "NUMERO_"),
    ("_UF", "_UNIDADE_FEDERATIVA"),
]


def _normalizar_nome(col: str) -> str:
    """UPPER + expansão de prefixos/sufixos comuns."""
    n = col.upper()
    for old, new in REGRAS:
        n = n.replace(old, new)
    return n


def processar(src: str, dest: str) -> None:
    df = spark.read.format("delta").table(src)
    df = df.toDF(*[_normalizar_nome(c) for c in df.columns])

    # Drop colunas obsoletas
    for c in ["DATA_HORA_BRONZE", "NOME_ARQUIVO", "_ID"]:
        if c in df.columns:
            df = df.drop(c)

    # Trim em strings
    for c, t in df.dtypes:
        if t == "string":
            df = df.withColumn(c, F.trim(F.col(c)))

    # Dedup
    df = df.dropDuplicates()

    # Auditoria silver
    df = (
        df.withColumn("NOME_ARQUIVO_BRONZE", F.lit(src))
          .withColumn("DATA_ARQUIVO_SILVER", F.current_timestamp())
    )

    df.write.format("delta").mode("overwrite").saveAsTable(dest)
    print(f"{dest} ok ({df.count()} linhas)")


# COMMAND ----------
TABELAS = [
    "apolice", "carro", "cliente", "endereco", "estado", "marca",
    "modelo", "municipio", "regiao", "sinistro", "telefone",
]

for t in TABELAS:
    processar(f"bronze.{t}", f"silver.{t}")

# COMMAND ----------
# MAGIC %sql SHOW TABLES IN silver;

# COMMAND ----------
# MAGIC %sql SELECT * FROM silver.apolice LIMIT 5;
