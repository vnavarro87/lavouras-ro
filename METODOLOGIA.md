# Metodologia

Este documento descreve as fontes, o tratamento e as limitações dos dados utilizados no projeto **Lavouras de Rondônia**. Tudo aqui é verificável em fontes públicas do IBGE.

## Fontes

| Dado | Fonte | Tabela SIDRA | Variável | Período |
|------|-------|-------------|----------|---------|
| Quantidade produzida (t) | IBGE / PAM | 1612 e 1613 | 214 | 2023 |
| Valor da produção (R$ mil) | IBGE / PAM | 1612 e 1613 | 215 | 2023 |
| Produtividade (kg/ha) | IBGE / PAM | 1612 e 1613 | 112 | 2023 |
| Área plantada (ha) | IBGE / PAM | 1612 | 109 | 2023 |
| Geometria municipal | IBGE / Malha Municipal | — | — | 2022 |

Tabela 1612: Produção Agrícola Municipal — Lavouras Temporárias (Soja, Milho).
Tabela 1613: Produção Agrícola Municipal — Lavouras Permanentes (Café, Cacau).

A PAM é a referência oficial brasileira para estatísticas de produção agrícola em nível municipal, com periodicidade anual.

## Culturas e códigos de produto

| Cultura | Tabela | Classificação | Código |
|---------|--------|--------------|--------|
| Soja | 1612 | c81 | 2713 |
| Milho | 1612 | c81 | 2711 |
| Café | 1613 | c82 | 2723 |
| Cacau | 1613 | c82 | 2722 |

## Coleta

A coleta é automatizada via API SIDRA (`apisidra.ibge.gov.br/values`). Cada variável é requisitada com filtro para nível de município (`n6`) restrito a Rondônia (`n3 11`).

O script de coleta está em [`coleta_geral.py`](coleta_geral.py).

## Disponibilidade de área plantada

A variável 109 (área plantada) está disponível na tabela 1612 (lavouras temporárias) para Soja e Milho. Para lavouras permanentes (tabela 1613), o IBGE não disponibiliza área plantada na mesma estrutura — por isso Café e Cacau não possuem essa coluna no dataset. O gráfico de dispersão para essas culturas usa produção × produtividade como alternativa.

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

## Validação

O script [`validate_data.py`](validate_data.py) executa as seguintes asserções após cada coleta:

- Presença de todas as colunas obrigatórias
- Exatamente 52 municípios (total oficial de RO, IBGE 2022)
- Ausência de municípios duplicados
- Ausência de valores negativos
- Match entre nomes de municípios no CSV e no GeoJSON

A validação falha com exit code 1 caso qualquer regra seja violada.

## Limitações conhecidas

1. **Granularidade temporal:** dados anuais; sem desagregação por safra ou intra-anual.
2. **Defasagem de publicação:** a PAM tem aproximadamente 1 ano de defasagem entre o ano de referência e a publicação oficial.
3. **Valores monetários:** em reais correntes do ano de referência. Comparações entre anos exigiriam deflacionamento — não aplicado neste projeto.
4. **Dados suprimidos:** células com sigilo estatístico são contabilizadas como zero, o que pode subestimar levemente totais agregados.
5. **Área de café e cacau:** não disponível na estrutura consultada da tabela 1613.

## Reprodutibilidade

```bash
pip install -r requirements.txt
python coleta_geral.py
python validate_data.py
streamlit run app.py
```
