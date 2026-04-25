# Mapa da Soja em Rondônia

Visualização interativa da produção de soja nos 52 municípios de Rondônia, a partir de dados públicos do IBGE (Pesquisa Agrícola Municipal — PAM 2023).

Construído em Python com Streamlit e Plotly. Os dados são coletados automaticamente da API SIDRA, validados e renderizados em um mapa coroplético com filtros por métrica (quantidade, produtividade, área plantada).

## O que o projeto mostra

- Mapa coroplético dos 52 municípios com escolha de métrica
- KPIs estaduais ou por município selecionado
- Top 10 produtores
- Dispersão "Área plantada × Produtividade" com média estadual destacada

## Como rodar

```bash
git clone <repo>
cd mapa_producao_ro
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
mapa_producao_ro/
├── app.py                       # Aplicação Streamlit
├── coleta_geral.py              # ETL via API SIDRA
├── validate_data.py             # Asserções de integridade
├── dados_agro_ro_master.csv     # Dataset gerado pela coleta
├── mapa_ro.json                 # Geometria municipal (IBGE)
├── METODOLOGIA.md               # Fontes, tratamento e limitações
├── requirements.txt
└── README.md
```

## Fontes e limitações

Dados: IBGE / PAM 2023 via API SIDRA (tabela 1612). Geometria: Malha Municipal IBGE 2022.

Os dados são **anuais e refletem o último ano fechado**. Não é informação em tempo real. Células suprimidas por sigilo estatístico são tratadas como zero para fins de visualização — o script de coleta imprime um relatório com a contagem afetada.

Detalhamento completo em [METODOLOGIA.md](METODOLOGIA.md).

## Sobre

Primeiro projeto público com foco em dados do agronegócio brasileiro. O objetivo é praticar pipeline ETL, visualização geoespacial e entrega reproduzível, sem prometer mais do que os dados públicos permitem.
