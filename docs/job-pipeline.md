# Job & Pipeline

## Job

Nome: `pipeline_seguradora_medalhao`
Compute: Serverless (padrão Free Edition)
Trigger: Manual (`Run now`)
Max concurrent runs: 1

## DAG

```
setup ──► landing ──► bronze ──► silver ──► gold
```

5 tasks com dependência linear. Cada task usa um notebook em `notebooks/`.

## Asset Bundle (`databricks_job.yml`)

Definição declarativa do Job versionada no repo. Permite recriar o Job em qualquer workspace via:

```bash
databricks bundle deploy --target dev
```

(Requer o Databricks CLI v0.200+ instalado e autenticado.)

Veja o arquivo [`databricks_job.yml`](../databricks_job.yml) na raiz do repo.

## Criação manual via UI (alternativa)

Se preferir não usar o CLI:

1. Databricks UI → **Jobs & Pipelines** → **Create Job**.
2. Nome: `pipeline_seguradora_medalhao`.
3. Adicionar 5 tasks (Type: Notebook), cada uma apontando para o notebook do Git Folder e com `Depends on` linkando à anterior.
4. Em `landing`, adicionar **Job parameter** `MONGODB_URI` (ou referenciar secret).
5. Save → Run now.
