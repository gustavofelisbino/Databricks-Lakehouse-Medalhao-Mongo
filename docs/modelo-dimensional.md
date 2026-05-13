# Modelo Dimensional (Gold)

Star schema baseado no modelo apresentado pelo professor (notebook 004), aplicando Ralph Kimball.

## Diagrama

```
                        ┌──────────────┐
                        │  dim_tempo   │
                        │  ─────────── │
                        │  Data (PK)   │
                        │  Ano, Mes,…  │
                        └──────┬───────┘
                               │
              ┌────────────────┴──────────────┐
              │                                │
       ┌──────┴─────────┐              ┌──────┴──────────┐
       │   dim_carro    │              │  dim_cliente    │
       │  ──────────────│              │  ────────────── │
       │  SK_CARRO (PK) │              │  SK_CLIENTE (PK)│
       │  PLACA, MARCA, │              │  CODIGO_CLIENTE,│
       │  MODELO, COR…  │              │  NOME, CPF…     │
       └──────┬─────────┘              └──────┬──────────┘
              │                                │
              │       ┌──────────────────┐     │
              │       │  fato_sinistro   │     │
              └───────┤  ──────────────  ├─────┘
                      │  FK_TEMPO        │
                      │  FK_LOCALIDADE   │
              ┌───────┤  FK_CARRO        │
              │       │  FK_CLIENTE      │
              │       │  QTDE_SINISTRO   │
       ┌──────┴───────┴──────┐
       │  dim_localidade     │
       │  ────────────────── │
       │  SK_LOCALIDADE (PK) │
       │  CODIGO_MUNICIPIO,  │
       │  NOME_MUNICIPIO,    │
       │  NOME_ESTADO,       │
       │  NOME_REGIAO        │
       └─────────────────────┘
```

## Dicionário

### `gold.dim_carro`

| Coluna | Tipo | Descrição |
|---|---|---|
| `SK_CARRO` | bigint identity | Surrogate key |
| `PLACA` | string | Placa do veículo (chave de negócio) |
| `MARCA` | string | Marca (vem de `silver.marca`) |
| `MODELO` | string | Modelo (vem de `silver.modelo`) |
| `COR` | string | Cor |
| `ANO` | int | Ano de fabricação |
| `CHASSI` | string | Chassi |

### `gold.dim_cliente`

| Coluna | Tipo | Descrição |
|---|---|---|
| `SK_CLIENTE` | bigint identity | Surrogate key |
| `CODIGO_CLIENTE` | int | Código natural do cliente |
| `NOME` | string | Nome completo |
| `CPF` | string | CPF (mantido como string para preservar zeros à esquerda) |
| `SEXO` | string | Sexo (M/F) |
| `DATA_NASCIMENTO` | date | Data de nascimento |

### `gold.dim_localidade`

| Coluna | Tipo | Descrição |
|---|---|---|
| `SK_LOCALIDADE` | bigint identity | Surrogate key |
| `CODIGO_MUNICIPIO` | int | Código IBGE do município |
| `NOME_MUNICIPIO` | string | Nome do município |
| `NOME_ESTADO` | string | Nome do estado |
| `NOME_REGIAO` | string | Região (Norte, Sul, etc.) |

### `gold.dim_tempo`

| Coluna | Tipo | Descrição |
|---|---|---|
| `Data` | date | Data (chave) |
| `Ano` | int | Ano |
| `Mes` | int | Mês (1-12) |
| `NomeMes` | string | Nome do mês em PT-BR |
| `Dia` | int | Dia do mês |
| `NomeDiaSemana` | string | Dia da semana em PT-BR |
| `NumeroDiaSemana` | int | 1=Domingo, 7=Sábado |

Range: `2023-01-01` a `2026-12-31`.

### `gold.fato_sinistro`

| Coluna | Tipo | Descrição |
|---|---|---|
| `FK_TEMPO` | date | FK → `dim_tempo.Data` |
| `FK_LOCALIDADE` | bigint | FK → `dim_localidade.SK_LOCALIDADE` |
| `FK_CARRO` | bigint | FK → `dim_carro.SK_CARRO` |
| `FK_CLIENTE` | bigint | FK → `dim_cliente.SK_CLIENTE` |
| `QTDE_SINISTRO` | int | Quantidade de sinistros no grão (dia × local × carro × cliente) |

**Grão:** 1 linha por (dia, localidade, carro, cliente) com `COUNT(1)` de sinistros.
