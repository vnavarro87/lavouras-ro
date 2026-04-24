# Agro Intelligence Hub | Rondônia

Solução de **Business Intelligence (BI) Executivo** focada na análise estratégica e georeferenciada do setor agropecuário do estado de Rondônia. O projeto utiliza uma narrativa de dados (storytelling) para guiar o usuário da visão macroeconômica estadual ao detalhamento técnico municipal.

## Estrutura de Navegação Estratégica

O dashboard é organizado em três pilares fundamentais que respondem às perguntas críticas do setor:

### 1. Visão Geográfica (O Onde)
Foco na distribuição espacial da produção. Permite identificar polos produtivos, líderes regionais e a capilaridade das principais culturas e rebanhos em todo o território rondoniense.

### 2. Análise de Performance (O Como)
Avaliação da eficiência técnica municipal. Utiliza uma Matriz de Performance que cruza Produtividade (Kg/Ha) vs. Escala (Ha), permitindo identificar especialistas de alta performance e gargalos tecnológicos relativos à média estadual.

### 3. Sazonalidade e Mercado (O Quando e o Quanto)
Monitoramento de ciclos produtivos e projeções financeiras. Integra um calendário de riscos climáticos e fitossanitários com um simulador dinâmico de Valor Bruto da Produção (VBP) baseado em cotações de mercado.

## Destaques Técnicos
- **KPIs em Tempo Real:** Visão imediata do PIB Agropecuário, VBP, Rebanho Total e Área Cultivada.
- **Pipeline de Dados Auditado:** Integração automatizada via API SIDRA (IBGE) com as tabelas PAM, PPM e PIB Municipal.
- **Arquitetura Executiva:** Interface minimalista desenvolvida em Python e Streamlit, focada em UX para tomada de decisão.

## Estrutura de Auditoria de Dados
Fontes oficiais utilizadas:
- IBGE Tabela 1612/1613 (Agricultura)
- IBGE Tabela 3939 (Pecuária)
- IBGE Tabela 74 (Leite)
- IBGE Tabela 5938 (PIB Municipal - Valor Adicionado Agropecuário)

---
*Desenvolvido para transformar dados públicos em inteligência estratégica para o agronegócio de Rondônia.*
