# Databricks notebook source
# COMMAND ----------
# MAGIC %md
# MAGIC # 00 — Setup do Ambiente
# MAGIC
# MAGIC Cria os schemas medalhão e os volumes de landing.
# MAGIC Idempotente — pode rodar várias vezes.

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.landing
# MAGIC   COMMENT 'Dados brutos extraídos do MongoDB (JSONL)';

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.landing.dados
# MAGIC   COMMENT 'JSONL gerado pela extração Mongo (output do notebook 01)';

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.landing.csv_raw
# MAGIC   COMMENT 'CSVs de origem para o seed (upload manual via UI)';

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.bronze
# MAGIC   COMMENT 'Bronze (Delta managed)';

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.silver
# MAGIC   COMMENT 'Silver (Delta managed, DQ aplicado)';

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.gold
# MAGIC   COMMENT 'Gold (modelo dimensional Ralph Kimball)';

# COMMAND ----------
# MAGIC %sql SHOW SCHEMAS IN workspace;
