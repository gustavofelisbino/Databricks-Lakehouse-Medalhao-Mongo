---
tags:
  - runbook
  - operação
  - databricks
  - passo a passo
---

# :material-play-circle: Runbook Databricks — Operação Ponta a Ponta

Tudo é feito pela **UI do Databricks Free Edition + MongoDB Atlas** (web).
Sem instalação local de Python ou ferramentas — apenas um navegador.

---

## :material-check-all: Pré-requisitos

!!! abstract "Antes de começar"
    - [x] Conta no **Databricks Free Edition** com Serverless habilitado
    - [x] Cluster **M0** no MongoDB Atlas configurado conforme [Setup MongoDB](setup-mongo.md)
    - [x] Connection string do Atlas em mãos (`mongodb+srv://...`)
    - [x] Repositório clonado/forkado no GitHub

---

## :material-numeric-1-circle: Conectar o Repositório no Databricks

```mermaid
flowchart LR
    A["Databricks Workspace"] -->|"Add → Git folder"| B["URL do GitHub"]
    B -->|"Provider: GitHub\nBranch: main"| C["Git Folder clonado\n/Workspace/Users/..."]
    style C fill:#6366f1,color:#fff,stroke:#4338ca
```

- [ ] **Workspace** → botão **Add** → **Git folder**
- [ ] **URL:** `https://github.com/gustavofelisbino/Databricks-Lakehouse-Medalhao-Mongo`
- [ ] **Provider:** GitHub · **Branch:** `main`
- [ ] Clique em **Create**

O clone aparecerá em:
```
/Workspace/Users/<seu-email>/Databricks-Lakehouse-Medalhao-Mongo/
```

---

## :material-numeric-2-circle: Configurar Credencial MongoDB

Escolha uma das opções:

=== "Opção A — Secret Scope (recomendado)"

    Seguro: a connection string não fica visível nos logs ou na UI.

    Em um terminal com **Databricks CLI** instalado:

    ```bash
    pip install databricks-cli
    databricks auth login --host https://<seu-workspace>.cloud.databricks.com
    databricks secrets create-scope mongo
    databricks secrets put-secret mongo uri
    # Cole a connection string completa quando solicitado
    ```

    !!! success "Verificar"
        ```bash
        databricks secrets list --scope mongo
        # Deve aparecer: uri
        ```

=== "Opção B — Job Parameter (100% UI)"

    Sem instalação de CLI. A string será passada como parâmetro do Job
    no Passo 5. O notebook lê automaticamente do widget se o secret não existir.

    Não é necessário fazer nada aqui — configure no Passo 5.

---

## :material-numeric-3-circle: Setup Inicial (executar uma vez)

!!! info "Esta etapa é executada apenas na primeira vez"
    Cria os schemas e volumes necessários no workspace.

- [ ] No Git Folder, abrir **`notebooks/00_setup_ambiente.py`**
- [ ] Clicar em **Run all** (ou ++shift+enter++ em cada célula)
- [ ] Verificar output: deve mostrar **4 schemas criados** + **2 volumes em `workspace`**
- [ ] Ir ao **Catalog Explorer** → `workspace` → schema `landing` → volume `csv_raw`
- [ ] Clicar em **Upload to this volume**
- [ ] Selecionar os **11 CSVs** de `data/raw/` do repositório local
- [ ] Abrir **`notebooks/00b_seed_csv_para_mongo.py`** → **Run all**
- [ ] Output esperado: 11 linhas `<collection>: N docs inseridos`
- [ ] Confirmar no Atlas: **Browse Collections** → banco `seguradora` deve ter **11 collections**

---

## :material-numeric-4-circle: Sanity Check da Extração

!!! tip "Validação manual antes de criar o Job"
    Execute o notebook de landing individualmente para confirmar que a conexão
    com o MongoDB está funcionando.

- [ ] Abrir **`notebooks/01_landing_extracao_mongo.py`** → **Run all**
- [ ] Output esperado: 11 linhas `<col>: N docs → /Volumes/.../<col>.json`
- [ ] Última célula: `dbutils.fs.ls(...)` deve mostrar **11 arquivos `.json`**

!!! failure "Se falhar aqui"
    O problema é na credencial ou no Network Access do Atlas.
    Consulte a seção [Troubleshooting](#troubleshooting) abaixo.

---

## :material-numeric-5-circle: Criar o Job

- [ ] UI → **Jobs & Pipelines** → **Create Job**
- [ ] Nome: `pipeline_seguradora_medalhao`
- [ ] Adicionar **5 tasks** com as configurações abaixo:

| # | Task name | Tipo | Notebook path | Depends on |
|---|-----------|------|---------------|------------|
| 1 | `setup` | Notebook | `notebooks/00_setup_ambiente` | *(nenhum)* |
| 2 | `landing` | Notebook | `notebooks/01_landing_extracao_mongo` | `setup` |
| 3 | `bronze` | Notebook | `notebooks/02_bronze_ingestao` | `landing` |
| 4 | `silver` | Notebook | `notebooks/03_silver_data_quality` | `bronze` |
| 5 | `gold` | Notebook | `notebooks/04_gold_dimensional` | `silver` |

Para cada task:

- [ ] **Compute:** Serverless
- [ ] **Max retries:** 1
- [ ] Na task `landing`: se usar **Opção B** (Job Parameter), adicionar:
      `MONGODB_URI = mongodb+srv://usuario:senha@cluster.mongodb.net/...`

- [ ] Clicar em **Save**

---

## :material-numeric-6-circle: Executar o Job

- [ ] No Job, clicar em **Run now** (topo da página)
- [ ] Acompanhar o DAG: cada bolinha vira verde quando a task conclui com sucesso
- [ ] Tempo total esperado: **3–8 minutos**

```mermaid
stateDiagram-v2
    [*] --> setup
    setup --> landing
    landing --> bronze
    bronze --> silver
    silver --> gold
    gold --> [*]
```

!!! tip "Cold start"
    O Serverless pode levar 30–90 segundos para inicializar na primeira execução.
    Execuções subsequentes no mesmo dia são mais rápidas.

---

## :material-numeric-7-circle: Validação

Em qualquer notebook ou no **SQL Editor** do Databricks:

```sql
-- Verificar schemas criados
SHOW SCHEMAS IN workspace;
-- Esperado: landing, bronze, silver, gold

-- Tabelas por camada
SHOW TABLES IN bronze;   -- 11 tabelas
SHOW TABLES IN silver;   -- 11 tabelas
SHOW TABLES IN gold;     -- 5 tabelas (4 dim + 1 fato)

-- Métricas da fato
SELECT COUNT(*) AS total_sinistros FROM gold.fato_sinistro;

-- Amostra da Silver (colunas em CAIXA_ALTA)
SELECT * FROM silver.apolice LIMIT 5;

-- Dimensão temporal (deve ter ~1461 dias)
SELECT COUNT(*) AS dias, MIN(Data) AS inicio, MAX(Data) AS fim
FROM gold.dim_tempo;

-- Query analítica completa
SELECT t.Ano, l.NOME_ESTADO, SUM(f.QTDE_SINISTRO) AS total
FROM gold.fato_sinistro f
INNER JOIN gold.dim_tempo       t ON f.FK_TEMPO      = t.Data
INNER JOIN gold.dim_localidade  l ON f.FK_LOCALIDADE = l.SK_LOCALIDADE
GROUP BY t.Ano, l.NOME_ESTADO
ORDER BY total DESC;
```

---

## :material-numeric-8-circle: Entrega no GitHub

- [ ] Push do branch `main` no GitHub
- [ ] Verificar **Actions** → workflow `Deploy MkDocs` deve ficar verde
- [ ] Documentação publicada em:  
      `https://gustavofelisbino.github.io/Databricks-Lakehouse-Medalhao-Mongo/`
- [ ] (Opcional) Fazer print do DAG verde do Job e incluir no README

---

## :material-bug-outline: Troubleshooting { #troubleshooting }

| Sintoma | Causa provável | Ação |
|---------|---------------|------|
| `pymongo.errors.ServerSelectionTimeoutError` | Network Access do Atlas não liberado | [Setup MongoDB](setup-mongo.md) → Passo 2: liberar `0.0.0.0/0` |
| `AssertionError: MONGODB_URI não configurado` | Secret e widget ambos ausentes | Configurar Secret Scope **ou** passar Job Parameter |
| `Authentication failed` | Senha incorreta ou URL-encoding necessário | Verificar usuário/senha; se contém `@:/?#`, trocar por caracteres simples |
| Task `gold` falha com `column not found` | Nome de coluna do Silver não bate com o SQL do Gold | Inspecionar `silver.sinistro` e ajustar nomes no notebook `04_gold_dimensional` |
| `AnalysisException: Table not found` | Task anterior não concluiu (schema não existe) | Verificar se a task `setup` concluiu com sucesso antes de rodar `landing` |
| Job lento (> 10 min) | Cold start do Serverless | Normal na 1ª execução do dia; aguardar ou rodar `setup` manualmente antes |
| `Cannot write to managed table` | Permissão de escrita no catálogo | Verificar que o usuário tem permissão no catálogo `workspace` |

!!! tip "Debug interativo"
    Para diagnosticar erros, execute cada notebook **manualmente** (Run all) antes
    de criar o Job. Isso isola a task com falha e exibe o stack trace completo.
