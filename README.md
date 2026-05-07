# Lavouras de Rondônia

Rondônia é um dos estados com maior expansão agrícola do Brasil na última década, mas a produção municipal é pouco visível fora dos relatórios do IBGE — tabelas brutas que não mostram concentração regional, disparidade de produtividade entre municípios vizinhos ou o peso de cada cultura na economia local.

Quis tornar esses dados navegáveis: qual município lidera em produtividade (não só em volume), qual o **preço médio implícito recebido** (R$/t) por município, quais municípios produzem muito mas com produtividade abaixo da média estadual.

## Relação com outros projetos

Este é o **panorama estático** do agro de Rondônia (PAM-IBGE 2023, anual, descritivo). Para análise de **risco de receita** com preço internacional e câmbio, ver [soja-milho-ro](https://github.com/vnavarro87/soja-milho-ro) — projeto irmão que cobre soja e milho com cotações CBOT, PTAX e basis municipal.

| Projeto | Pergunta que responde | Frequência |
|---------|----------------------|------------|
| **lavouras-ro** (este) | Onde está a produção, quem produz bem, qual preço médio | Anual (PAM) |
| **soja-milho-ro** | Quanto vale a produção hoje, em quanto está o break-even, qual o risco cambial | Diária (CBOT/PTAX) |

## Decisões de design

**4 culturas, não todas as disponíveis no PAM**
Soja, milho, café e cacau foram escolhidas por relevância econômica e regional — não por exaustividade. Incluir todas as culturas do PAM tornaria a navegação genérica demais para ser útil.

**Mapa coroplético como visualização principal**
Gráficos de barra mostram ranking; o mapa mostra padrão espacial. Para entender por que municípios vizinhos têm produtividades tão diferentes, a dimensão geográfica é insubstituível.

**API SIDRA em vez de CSVs baixados manualmente**
Reprodutibilidade: qualquer pessoa pode rodar `coleta_geral.py` e obter os mesmos dados, sem depender de arquivo que pode ficar desatualizado no repo.

**Plotly em vez de Folium para o mapa**
Integração nativa com Streamlit sem necessidade de `st.components`. Renderização mais rápida para 52 municípios e consistência visual com os demais gráficos do app.

**Coleta e validação em scripts separados**
Permite rodar `validate_data.py` sem refazer o ETL. Útil para checar integridade depois de ajustes no tratamento sem custo de nova chamada à API.

**Células com sigilo estatístico tratadas como zero**
O IBGE suprime valores de municípios com poucos produtores para proteger dados individuais. A alternativa seria excluir esses municípios do mapa — mas isso criaria buracos visuais que seriam lidos como ausência de dado, não como sigilo. Optei por zero com nota explícita na metodologia.

## Stack

- **Python** + **Streamlit** + **Plotly**
- **IBGE/SIDRA** — PAM 2023, tabelas 1612 (lavouras temporárias) e 1613 (lavouras permanentes)
- Malha Municipal IBGE 2022

## Como rodar

```bash
git clone https://github.com/vnavarro87/lavouras-ro.git
cd lavouras-ro
pip install -r requirements.txt
streamlit run app.py
```

Para reexecutar a coleta do zero:

```bash
python coleta_geral.py
python validate_data.py
```

## Validação de dados

Cada número é defensável pela identidade física **Quantidade ≈ Área × Produtividade** (apenas para soja/milho — PAM 1613 não publica área plantada de lavouras permanentes na mesma estrutura). O script `validate_data.py` roda 4 níveis de checagem:

1. **Estrutural** — 52 municípios, sem duplicatas, sem negativos, match CSV ↔ GeoJSON
2. **Consistência interna** — Quantidade ≈ Área × Produtividade (tolerância 12%, cobre Área Plantada vs. Área Colhida)
3. **Produtividade plausível** — soja 2,5–4,5 / milho 1,5–6,5 / café 0,8–5,0 / cacau 0,3–2,5 t/ha
4. **Coerência cruzada** — Quantidade > 0 ↔ Valor > 0 (não pode haver produção sem registro de valor monetário)

Saída em formato CI-friendly (exit code 0 = aprovado; 1 = violação com município identificado). Quando o IBGE publicar PAM 2024, basta rerodar.

## Estrutura

```
lavouras-ro/
├── app.py                       # Aplicação Streamlit
├── coleta_geral.py              # ETL via API SIDRA
├── validate_data.py             # Asserções de integridade
├── dados_agro_ro_master.csv     # Dataset gerado pela coleta
├── mapa_ro.json                 # Geometria municipal (IBGE 2022)
├── METODOLOGIA.md               # Fontes, tratamento e limitações
├── requirements.txt
└── README.md
```

## Limitações conhecidas

- **Área plantada ausente para café e cacau.** As tabelas de lavouras permanentes do PAM não separam área plantada da área em produção da mesma forma que as temporárias. Produtividade para essas culturas usa a métrica disponível, não o ideal.

- **Sem desagregação intra-anual.** PAM é anual. Sazonalidade, colheita parcial e variação de preço ao longo do ano não estão capturados — para risco e timing, ver [soja-milho-ro](https://github.com/vnavarro87/soja-milho-ro).

- **Valores monetários em reais correntes.** Não há deflação. Comparações de valor entre anos diferentes exigiriam ajuste que não implementei.

- **Células com sigilo estatístico aparecem como zero.** Municípios com poucos produtores têm dados suprimidos pelo IBGE para preservar identidade individual. No CSV atual, sigilo é indistinguível de zero verdadeiro — TODO documentado no `coleta_geral.py` para refatorar o pipeline e gerar um arquivo `sigilo_ro.csv` separado. A legenda do mapa avisa explicitamente sobre essa ambiguidade.

- **Preço médio implícito ≠ preço de mercado.** O preço R$/t exibido vem de Valor PAM ÷ Quantidade — é referência IBGE, agregada anual. Não é preço spot recebido em uma negociação específica.

- **Ranking de produtividade tem corte mínimo de relevância.** Município com produção residual (< 0,5% do total estadual ou < 50 t) é excluído do ranking de eficiência — sem isso, um município com 2 t e produtividade alta apareceria como referência, distorcendo a leitura.

Detalhamento completo em [METODOLOGIA.md](METODOLOGIA.md).

## Sobre

Primeiro projeto de uma série sobre o agronegócio de Rondônia. A pergunta de partida era simples: onde está, de fato, a produção agrícola do estado — e quão diferente é um município do outro?

Implementação acelerada com uso de Claude Code como copiloto. Definição do problema, escolha de fontes, decisões de arquitetura, validações de integridade e tratamento de edge cases conduzidos por mim.

## Limitações de escopo

Este projeto é deliberadamente limitado a um corte (PAM 2023, 4 culturas, RO) para entregar análise reproduzível e validada. Análises temporais e cruzamento climático são tratados como projetos separados.

## Licença

Copyright (C) 2026 Vinicius Navarro.

Este projeto está licenciado sob a [GNU Affero General Public License v3.0](LICENSE). Em resumo: você pode usar, estudar, modificar e redistribuir, mas qualquer trabalho derivado — inclusive uso como serviço de rede — precisa ser disponibilizado sob a mesma licença. Para licenciamento comercial sob outros termos, entre em contato.
