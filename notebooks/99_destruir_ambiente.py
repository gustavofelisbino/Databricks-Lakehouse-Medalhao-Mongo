# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # 99 — Destruir Ambiente (limpeza opcional)
# MAGIC
# MAGIC **ATENÇÃO:** apaga TODOS os schemas e dados das camadas medalhão.
# MAGIC Use apenas para resetar o ambiente em desenvolvimento.

# COMMAND ----------
# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS workspace.gold CASCADE;

# COMMAND ----------
# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS workspace.silver CASCADE;

# COMMAND ----------
# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS workspace.bronze CASCADE;

# COMMAND ----------
# MAGIC %sql
# MAGIC DROP SCHEMA IF EXISTS workspace.landing CASCADE;

# COMMAND ----------
# MAGIC %sql SHOW SCHEMAS IN workspace;
