# MEMÓRIA ESTRATÉGICA - Portfólio Vinicius Navarro

## 🎯 Objetivo dos Projetos (Lavouras RO / Commodities RO / Pecuária RO)
Demonstrar maturidade técnica e analítica para recrutadores e gestores. São peças de portfólio público, construídas por uma única pessoa, focadas em dados públicos e deploy gratuito (Streamlit).

---

## 🛠️ Regras de Engajamento (Postura da IA)

### O que os projetos SÃO:
- Peças de portfólio técnico (LinkedIn/GitHub).
- Baseados exclusivamente em **dados públicos** (IBGE, CONAB, BCB, yfinance).
- Focados em **Python + Streamlit**.
- Demonstrativos de capacidade analítica e narrativa de dados.

### O que os projetos NÃO SÃO:
- Não são SaaS ou Startups.
- Não são consultoria financeira (sem recomendações operacionais).
- Não competem com plataformas comerciais (Bloomberg, AgroTools).
- Não modelam decisões de manejo (plantio, pragas, seguro).

---

## 📏 Filtros para Sugestões e Melhorias

1. **Esforço (1-3h):** A implementação deve ser rápida. Se exigir semanas ou pipelines complexos, está fora.
2. **Defensibilidade:** Toda métrica deve ter fonte rastreável e explicação simples. Sem fórmulas inventadas.
3. **Linguagem Descritiva:** Nunca sugerir ações ("compre", "venda", "trave"). Apenas descrever o estado dos dados ("mínima histórica", "correlação de X%").
4. **Curadoria > Expansão:** Se estiver poluído, a solução é cortar ou reorganizar, não criar novos módulos.
5. **Foco Narrativo:** Priorizar a "história" que os dados contam sobre a economia regional de RO.
6. **Reaproveitamento:** Sempre verificar o código existente antes de propor novas funções.

---

## 🧠 Papel da IA
- **Sounding board** para teses econômicas (basis, terms of trade).
- **Crítico técnico** de métodos e fontes.
- **Provocador narrativo** (o que falta na história do dado?).
- **Validador de fontes** públicas.

---
*Documento atualizado em 25/04/2026 para alinhar a parceria IA-Humano.*

---

## 🧭 Ideias para projetos futuros do portfólio

Itens **não comprometidos publicamente** — não aparecem em README/blog/LinkedIn como promessa, ficam aqui apenas como sementes.

### Lavouras-RO (este projeto) — ideias para próxima iteração

- **Refatoração do pipeline para preservar sigilo estatístico.** Hoje os 4 scripts de coleta (`coleta_geral.py`, `coleta_cafe.py`, etc.) consolidam todos os códigos especiais do SIDRA como 0. Um pipeline unificado poderia gerar um arquivo `sigilo_ro.csv` paralelo com a flag por município/cultura/variável. O app distinguiria visualmente sigilo (textura/hachura) de zero verdadeiro (cinza sólido). Esforço estimado: 4–6h.

- **Análise temporal PAM 2018–2023** como projeto separado ("Tendências do agro de RO"). Permite responder: quem cresceu mais, quem despencou, aceleração vs estagnação. ~96 chamadas SIDRA (6 anos × 4 culturas × 4 variáveis). Esforço estimado: 1 fim de semana.

### Projetos novos planejados

- **Pecuaria-RO** — boi gordo, leite, carne. Já sinalizado em outros memórias.
- **Hedge & Sazonalidade RO** — soja + safrinha de milho combinados (CPR, NDF, put B3).
- **Clima e Produtividade RO** — INMET/CHIRPS cruzado com produção municipal.

### Itens herdados de iterações anteriores (avaliar relevância)

- Análise de Lag de Preços (Dólar → Boi Gordo) — fará sentido em pecuaria-ro.
- Ponto de Equilíbrio (Break-even) por região de RO — já implementado em soja-milho-ro.
- Cenários de Estresse (Seca no Madeira, Alta de Frete) — parcialmente atendido por choque de frete em soja-milho-ro.
