# Agro Intelligence Hub | Rondônia

Solução de Business Intelligence (BI) focada na análise estratégica e georeferenciada do setor agropecuário do estado de Rondônia. O projeto integra dados físicos de produção com métricas econômicas oficiais para oferecer uma visão de 360 graus da competitividade e do impacto regional do agronegócio.

## Destaques do Projeto
- **Pipeline de Dados Incontestável:** Consumo direto via API SIDRA (IBGE) das tabelas PAM (Agricultura), PPM (Pecuária/Leite) e PIB Municipal.
- **Matriz de Performance e Eficiência:** Visualização comparativa de produtividade (Kg/Ha) vs. Escala (Ha), identificando gargalos e potenciais por município.
- **Diferenciação Pecuária:** Separação técnica entre rebanho de corte (Efetivo Bovino) e rebanho de leite (Produção em Litros).
- **Análise de Sazonalidade e Riscos:** Calendário agrícola dinâmico cruzado com histórico de precipitação e alertas fitossanitários mensais.
- **Relevância Econômica Real:** Cálculo da participação de cada cultura no PIB Agropecuário municipal, utilizando dados oficiais de faturamento.

## Tecnologias e Ferramentas
- **Linguagem:** Python 3.10+
- **Interface:** Streamlit (UX Minimalista com Foco em Dados)
- **Visualização:** Plotly (Mapas GeoJSON e Gráficos Interativos)
- **Engenharia de Dados:** Pandas e Requests (Automação de ETL via API)

## Estrutura de Auditoria de Dados
Este projeto preza pela integridade da informação. As fontes utilizadas são:
- **IBGE Tabela 1612/1613:** Produção Agrícola Municipal (Soja, Milho, Café e Cacau).
- **IBGE Tabela 3939:** Efetivo dos Rebanhos.
- **IBGE Tabela 74:** Produção de Origem Animal (Leite).
- **IBGE Tabela 5938:** PIB dos Municípios (Valor Adicionado Bruto da Agropecuária).

## Como Executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute o app: `streamlit run app.py`

---
*Desenvolvido para transformar dados públicos em inteligência estratégica para o agronegócio de Rondônia.*
