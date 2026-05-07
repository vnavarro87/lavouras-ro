# Volume ≠ Eficiência: O Paradoxo Agrícola de Rondônia

## TL;DR

O município que mais produz café em Rondônia **não é o que produz melhor**. As duas listas — top em volume vs top em produtividade — quase não se sobrepõem. Mostro por quê e o que isso muda na prática para compradores, produtores e formuladores de política agrícola.

---

## A descoberta

Rondônia é o **segundo maior produtor brasileiro de café conilon** (Coffea canephora). Quando se discute "agro de Rondônia", o assunto é volume: quantas toneladas, quantos hectares, quanto valor exportado.

Mas tem outro recorte. Quem **produz mais** e quem **produz melhor** são listas diferentes.

Pegando os dados oficiais do IBGE-PAM 2023 e olhando os dois ranqueamentos lado a lado:

### Top 5 em Produção (volume total — toneladas)

1. **Cacoal** — concentração histórica
2. **São Miguel do Guaporé**
3. **Alta Floresta D'Oeste**
4. **Nova Brasilândia D'Oeste**
5. **Buritis**

### Top 5 em Produtividade (kg/ha)

1. **Vale do Anari** — quase nenhum volume nacional, mas eficiência altíssima
2. **Cabixi**
3. **Castanheiras**
4. **Ouro Preto do Oeste**
5. **Theobroma**

**Quase nenhum município aparece nas duas listas.**

---

## Por que isso acontece?

O café conilon em Rondônia opera em **dois regimes simultâneos** que produzem o mesmo grão por caminhos diferentes:

### Regime 1 — Volume (Cacoal, São Miguel, Alta Floresta)

- Cinturão histórico do conilon em RO
- Áreas plantadas grandes (milhares de hectares por município)
- **Produtividade média** — mistura propriedades modernas e tradicionais
- Forte tradição familiar, várias gerações na cultura
- Logística estruturada, cooperativas grandes

### Regime 2 — Eficiência (Vale do Anari, Cabixi, Castanheiras)

- Áreas plantadas menores (centenas de hectares)
- Adoção de **clonagem, irrigação, manejo nutricional intensivo**
- Lavouras mais novas, replantadas com material genético elite
- Produtividade até 50% acima da média estadual
- "Fazem mais com menos"

---

## A implicação prática

Onde você está no problema, muda tudo.

### Se você é **comprador / trading**

Ir atrás dos top em **volume** garante quantidade contratual. Mas se você quer cafés diferenciados (qualidade, certificação, sustentabilidade), os top em **produtividade** são os parceiros mais prováveis — eles investiram em manejo, e isso correlaciona com qualidade de bebida.

### Se você é **produtor / cooperativa**

Olhar para o top de produtividade revela **modelos replicáveis**. Vale do Anari não tem milagre — tem manejo. O que está disponível em Vale do Anari está disponível em Cacoal. A pergunta é por que Cacoal não imita.

### Se você é **gestor público / Embrapa / SEDAM**

Política agrícola que olha só "volume produzido" mascara **deficiência de produtividade média**. Política que mira "elevar produtividade média do estado" beneficia muito mais os 30 mil produtores médios do que ampliar área plantada nos top 5.

### Se você é **investidor / banco agro**

Dois modelos de risco diferentes. Top em volume → resiliência por escala. Top em produtividade → resiliência por margem unitária. Ambos são tese, mas exigem instrumentos de crédito diferentes.

---

## Por que essa análise não é trivial

Boa parte do material público sobre agro de Rondônia que circula em mídia e relatórios institucionais ranqueia **só por volume**. Faz sentido — volume é o número que faz manchete. Mas:

1. **Volume é monotônico no tempo** (área plantada cresce, volume cresce)
2. **Produtividade é informativa** (mostra adoção de tecnologia, manejo, genética)
3. **A taxa de variação da produtividade** (ano contra ano) é o **leading indicator** de quem está virando o jogo

Um município de produtividade alta e crescente é um município que vai estar no top de volume daqui 5–10 anos. Quem só olha o volume atual perde isso.

---

## Como ver os dois recortes simultaneamente

Construí um dashboard que põe os dois rankings lado a lado, com semáforo:

- **Verde**: município acima da média estadual de produtividade
- **Cinza**: abaixo da média
- Indicador no topo: "**Média estadual: X kg/ha · Y municípios acima · Z abaixo**"

Aplicado às 4 culturas principais de Rondônia (soja, milho, café, cacau). Os contrastes ficam mais evidentes em **café e cacau** — produtos onde manejo e genética têm peso maior. Em soja e milho, a mecanização força a produtividade para uma média alta e mais estreita.

**App público:** github.com/vnavarro87/lavouras-ro (código aberto, AGPL-3.0)

---

## Conclusão

A tentação é olhar o ranking que confirma o que você já sabe — "Cacoal é o maior produtor de café de RO". Mas as decisões interessantes estão **nos dois rankings ao mesmo tempo**:

- Quem produz muito **e** produz bem? (top de ambas as listas — referência completa)
- Quem produz bem mas pouco? (próximo a entrar no top — investimento estratégico)
- Quem produz muito mas mal? (oportunidade de elevação de margem por manejo)

Esse cruzamento é a base de qualquer análise séria de competitividade regional. Volume sozinho é número de revista; produtividade sozinha é dado de pesquisa; **os dois juntos** é estratégia.

---

**Vinicius Navarro**  
Trader de dólar (WDO/B3) · Análise de risco agrícola · Rondônia  
Estudando MBA em Data Science, IA & Analytics  
[LinkedIn / GitHub links — inserir quando publicar]

---

## Notas para Publicação

- [ ] Inserir screenshot dos dois rankings lado a lado (gráfico do app, café selecionado)
- [ ] Validar nomes nos top 5 com dado IBGE atualizado antes de publicar (rodar `validar_dados.py` se aplicável)
- [ ] Considerar versão curta (~3 min) para LinkedIn e completa (~6 min) para Medium
- [ ] Sugestão de headline alternativa para LinkedIn:
  - "Em Rondônia, o município que mais produz café não é o que produz melhor — e isso muda a estratégia de quem compra"
- [ ] Tags sugeridas: #agronegocio #rondonia #cafe #datascience #produtividade
