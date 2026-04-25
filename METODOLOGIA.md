# Metodologia

Este documento descreve as fontes, o tratamento e as limitações dos dados utilizados no projeto **Mapa da Soja em Rondônia**. Tudo aqui é verificável em fontes públicas do IBGE.

## Fontes

| Dado | Fonte | Tabela SIDRA | Período |
|------|-------|--------------|---------|
| Quantidade produzida (t) | IBGE / PAM | 1612, variável 214 | Último ano disponível (2023) |
| Valor da produção (R$ mil) | IBGE / PAM | 1612, variável 215 | 2023 |
| Produtividade (kg/ha) | IBGE / PAM | 1612, variável 112 | 2023 |
| Área plantada (ha) | IBGE / PAM | 1612, variável 109 | 2023 |
| Geometria municipal | IBGE / Malha Municipal | — | 2022 |

A Pesquisa Agrícola Municipal (PAM) é a referência oficial brasileira para estatísticas de produção agrícola em nível municipal, com periodicidade anual.

## Coleta

A coleta é automatizada via API SIDRA (`apisidra.ibge.gov.br/values`). Cada variável é requisitada com filtro para nível geográfico de município (`n6`) restrito a Rondônia (`n3 11`), produto Soja (código 2713 na classificação `c81`).

O script de coleta está em [`coleta_geral.py`](coleta_geral.py).

## Tratamento de dados ausentes ou suprimidos

O SIDRA utiliza códigos especiais quando o valor numérico não está disponível:

| Código | Significado |
|--------|-------------|
| `-` | Fenômeno não existe |
| `..` | Não se aplica |
| `...` | Dado não disponível |
| `X` | Dado omitido por sigilo estatístico |
| `0` | Zero verdadeiro |

**Limitação assumida:** após a conversão numérica, todos os códigos especiais são tratados como `0` para fins de visualização. O script de coleta imprime um relatório com a contagem de células afetadas por variável, permitindo auditoria.

Em projetos futuros pretendo manter colunas de status separadas para diferenciar "zero verdadeiro" de "suprimido por sigilo".

## Validação

O script [`validate_data.py`](validate_data.py) executa asserções básicas após cada coleta:

- Presença de todas as colunas obrigatórias
- Total de 52 municípios (IBGE 2022)
- Ausência de duplicatas
- Ausência de valores negativos
- Match entre nomes de municípios no CSV e no GeoJSON

A validação falha (exit code 1) caso qualquer regra seja violada.

## Limitações conhecidas

1. **Granularidade temporal:** os dados são anuais; não há desagregação por safra ou intra-anual.
2. **Defasagem:** a PAM tem cerca de 1 ano de defasagem entre o ano de referência e a publicação.
3. **Valores monetários:** estão em reais correntes do ano de referência. Comparações entre anos exigiriam deflacionamento (não aplicado neste projeto).
4. **Dados suprimidos:** células com sigilo estatístico são contabilizadas como zero, o que pode subestimar levemente totais agregados.

## Reprodutibilidade

```bash
pip install -r requirements.txt
python coleta_geral.py
python validate_data.py
streamlit run app.py
```
