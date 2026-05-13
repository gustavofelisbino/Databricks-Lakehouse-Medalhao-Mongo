---
tags:
  - mongodb
  - atlas
  - setup
  - credenciais
---

# :simple-mongodb: Setup MongoDB Atlas

Guia passo a passo para criar e configurar o cluster **MongoDB Atlas M0** (gratuito)
que servirá como fonte de dados do pipeline.

---

## :material-map-marker-path: Visão Geral

```mermaid
flowchart LR
    A["1. Criar cluster M0"] --> B["2. Liberar Network Access\n0.0.0.0/0"]
    B --> C["3. Criar usuário\ncom senha"]
    C --> D["4. Obter\nconnection string"]
    D --> E["5. Testar conexão\nem notebook"]
    style E fill:#15803d,color:#fff,stroke:#166534
```

---

## :material-numeric-1-circle: Criar Cluster M0

- [ ] Acesse [cloud.mongodb.com](https://cloud.mongodb.com) e faça login
- [ ] Clique em **Build a Database**
- [ ] Selecione **M0 Free** (512 MB — mais que suficiente para uso acadêmico)
- [ ] Escolha a região mais próxima:

=== "Brasil (recomendado)"

    **Provider:** AWS · **Region:** `sa-east-1` (São Paulo)

    Menor latência para conexões do Brasil. Caso não disponível no Free Tier,
    use `us-east-1`.

=== "EUA (alternativa)"

    **Provider:** AWS · **Region:** `us-east-1` (N. Virginia)

    Sempre disponível no M0. Latência levemente maior, mas imperceptível para
    volumes acadêmicos.

- [ ] Clique em **Create Deployment** e aguarde o provisionamento (~2 min)

---

## :material-numeric-2-circle: Liberar Network Access

!!! warning "Passo obrigatório"
    Sem liberar o Network Access, o Databricks não conseguirá conectar ao Atlas —
    o notebook `01_landing` falhará com `ServerSelectionTimeoutError`.

- [ ] Menu lateral → **Security → Network Access**
- [ ] Clique em **Add IP Address**
- [ ] Selecione **Allow Access from Anywhere** → IP: `0.0.0.0/0`
- [ ] Clique em **Confirm**

!!! note "Uso acadêmico"
    `0.0.0.0/0` é adequado para projetos acadêmicos. Em produção, restrinja ao
    CIDR do seu workspace Databricks ou use Private Link.

---

## :material-numeric-3-circle: Criar Usuário do Banco

- [ ] Menu lateral → **Security → Database Access**
- [ ] Clique em **Add New Database User**
- [ ] **Authentication Method:** Password
- [ ] Defina `<username>` e `<password>`
- [ ] **Built-in Role:** `Read and write to any database`
- [ ] Clique em **Add User**

!!! danger "Atenção à senha"
    Evite caracteres especiais na senha: `@ : / ? # [ ] @`  
    Esses caracteres precisam de URL-encoding na connection string e podem causar
    erros difíceis de diagnosticar.

    **Recomendação:** use apenas letras, números e `_` ou `-`.

---

## :material-numeric-4-circle: Obter a Connection String

- [ ] Menu lateral → **Clusters** → no seu cluster, clique em **Connect**
- [ ] Selecione **Drivers** → **Python** (versão 3.12+)
- [ ] Copie a connection string no formato:

```
mongodb+srv://<username>:<password>@<cluster-host>/?retryWrites=true&w=majority&appName=<app>
```

- [ ] Substitua `<username>` e `<password>` pelos valores reais
- [ ] Guarde essa string — será usada como `MONGODB_URI`

---

## :material-numeric-5-circle: Testar a Conexão

Antes de configurar o Job, valide a connection string diretamente em um notebook
do Databricks:

```python
%pip install pymongo
dbutils.library.restartPython()

from pymongo import MongoClient

# Substitua pela sua connection string real
MONGODB_URI = "mongodb+srv://usuario:senha@cluster.mongodb.net/"

c = MongoClient(MONGODB_URI)
resultado = c.admin.command("ping")
print(resultado)
# Esperado: {'ok': 1.0}

# Listar collections do banco seguradora
db = c["seguradora"]
print(db.list_collection_names())
```

!!! success "Conexão bem-sucedida"
    Se `{'ok': 1.0}` aparecer no output, a conexão está funcionando.

!!! failure "Falha na conexão"
    Se receber `ServerSelectionTimeoutError`, verifique:

    1. Network Access liberado (`0.0.0.0/0`) — Passo 2
    2. Usuário e senha corretos — Passo 3
    3. Connection string sem espaços extras ou caracteres inválidos

---

## :material-key-variant: Configurando a Credencial no Databricks

=== "Secret Scope (recomendado)"

    O Secret Scope armazena a connection string de forma segura, sem expor
    em código ou parâmetros visíveis:

    ```bash
    # Instalar o Databricks CLI (se necessário)
    pip install databricks-cli

    # Autenticar no workspace
    databricks auth login --host https://<seu-workspace>.cloud.databricks.com

    # Criar o scope
    databricks secrets create-scope mongo

    # Adicionar a secret
    databricks secrets put-secret mongo uri
    # Cole a connection string quando solicitado e pressione Enter
    ```

    No notebook, a secret é lida com:

    ```python
    uri = dbutils.secrets.get(scope="mongo", key="uri")
    ```

=== "Job Parameter (fallback UI)"

    Se preferir não usar o CLI, passe a connection string como parâmetro do Job:

    - [ ] No Job, vá em **Parameters** → **Add**
    - [ ] Key: `MONGODB_URI`
    - [ ] Value: `mongodb+srv://usuario:senha@cluster.mongodb.net/...`

    !!! warning "Visibilidade"
        Job Parameters são visíveis nos logs de execução e na UI do Job.
        Prefira Secret Scope para projetos com dados sensíveis.

    O notebook lê automaticamente via widget:

    ```python
    # Prioridade: Secret Scope > Job Parameter/Widget
    try:
        uri = dbutils.secrets.get(scope="mongo", key="uri")
    except Exception:
        uri = dbutils.widgets.get("MONGODB_URI")
    ```
