# Lavouras de Rondônia

Visualização interativa da produção agrícola nos 52 municípios de Rondônia, a partir de dados públicos do IBGE (Pesquisa Agrícola Municipal — PAM 2023).

Cobre quatro culturas: **Soja**, **Milho**, **Café** e **Cacau** — as principais lavouras do estado em volume, valor e relevância regional.

Construído em Python com Streamlit e Plotly. Os dados são coletados automaticamente da API SIDRA, validados e renderizados em mapa coroplético com filtros por cultura e métrica.

## O que o projeto mostra

- Mapa dos 52 municípios com seleção de cultura e métrica (quantidade, produtividade, valor)
- KPIs estaduais ou por município selecionado
- Top 10 produtores por cultura
- Dispersão produção × produtividade com média estadual destacada
- Contexto narrativo por cultura (por que ela importa em RO)

## Como rodar

```bash
git clone https://github.com/vnavarro87/mapa-soja-ro.git
cd mapa-soja-ro
pip install -r requirements.txt
streamlit run app.py
```

Para reexecutar a coleta a partir do SIDRA:

```bash
python coleta_geral.py
python validate_data.py
```

## Estrutura

```
mapa-soja-ro/
├── app.py                       # Aplicação Streamlit
├── coleta_geral.py              # ETL via API SIDRA
├── validate_data.py             # Asserções de integridade
├── dados_agro_ro_master.csv     # Dataset gerado pela coleta
├── mapa_ro.json                 # Geometria municipal (IBGE 2022)
├── METODOLOGIA.md               # Fontes, tratamento e limitações
├── requirements.txt
└── README.md
```

## Culturas e fontes

| Cultura | Tabela SIDRA | Tipo |
|---------|-------------|------|
| Soja | 1612 | Lavoura temporária |
| Milho | 1612 | Lavoura temporária |
| Café | 1613 | Lavoura permanente |
| Cacau | 1613 | Lavoura permanente |

Período de referência: PAM 2023 (último ano fechado disponível).
Geometria: Malha Municipal IBGE 2022.

Detalhamento completo em [METODOLOGIA.md](METODOLOGIA.md).

## Limitações conhecidas

- Dados anuais — sem desagregação intra-anual
- Café e Cacau não possuem dados de área plantada nas tabelas consultadas
- Valores monetários em reais correntes do ano de referência
- Células com sigilo estatístico tratadas como zero (ver METODOLOGIA.md)

## Sobre

Projeto de portfólio com foco em dados públicos do agronegócio brasileiro. Objetivo: praticar pipeline ETL com API pública, visualização geoespacial e entrega reproduzível — sem prometer mais do que os dados permitem.
