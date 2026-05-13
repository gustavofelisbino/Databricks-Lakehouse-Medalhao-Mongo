# Setup MongoDB Atlas

## 1. Criar cluster M0

- Login em <https://cloud.mongodb.com>.
- **Build a Database** → **M0 Free** → escolher região (preferência: `sa-east-1` São Paulo ou `us-east-1` N. Virginia).
- **Create Deployment**.

## 2. Liberar Network Access

- Menu lateral → **Security → Network Access** → **Add IP Address**.
- **Allow Access from Anywhere** (`0.0.0.0/0`) → **Confirm**.

> Para uso acadêmico está ok. Em produção, restringir CIDR.

## 3. Criar usuário do banco

- **Security → Database Access** → **Add New Database User**.
- Authentication: Password.
- Built-in Role: `Read and write to any database` (ou `Atlas admin`).
- Anote `<username>` e `<password>` — evite caracteres especiais (`@:/?#`) na senha para evitar URL-encoding.

## 4. Pegar a connection string

- Menu lateral → **Clusters** → no cluster, clicar **Connect**.
- **Drivers** → Python 3.12+.
- Copiar string no formato:
  ```
  mongodb+srv://<username>:<password>@<cluster-host>/?retryWrites=true&w=majority&appName=<app>
  ```
- Substituir `<username>` e `<password>` reais.

## 5. Teste rápido (opcional)

No próprio Databricks (em qualquer notebook):

```python
%pip install pymongo
dbutils.library.restartPython()
from pymongo import MongoClient
c = MongoClient("mongodb+srv://USER:PASS@HOST/")
print(c.admin.command("ping"))
# Esperado: {'ok': 1.0}
```
