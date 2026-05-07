# Choropleth Defensável em Streamlit: O Problema Que Ninguém Comenta

## TL;DR

Mapa coroplético em Plotly/Streamlit pintando só municípios com dado parece bom — até alguém perguntar "esse município preto não pertence ao estado, ou não tem dado?". Mostro o padrão de **duas camadas** (silhueta cinza + Viridis nos produtores) que resolve essa ambiguidade visual com 30 linhas de código.

---

## O problema

Você tem dados de produção agrícola por município. Quer fazer um mapa interativo. Pega `plotly.express.choropleth_map`, passa o GeoJSON do estado, pinta. Em 5 minutos tem isso:

```python
fig = px.choropleth_map(
    df, geojson=geojson, locations="Municipio",
    featureidkey="properties.name",
    color="Producao_Toneladas",
    color_continuous_scale="Viridis",
    map_style="carto-darkmatter", zoom=5.6,
    center={"lat": -10.9, "lon": -62.8},
)
```

Bonito. Você publica.

**Aí alguém abre o app e pergunta:**

> "Esses municípios pretos não produzem ou não pertencem a Rondônia? Não consigo ver o limite do estado."

E você nota: **o background do map_style escurece tudo igual** — município sem dado fica visualmente indistinguível da floresta amazônica ou do estado vizinho.

Pior: se a escala for **Viridis**, valores próximos de zero ficam **roxo escuro**, que é parecido com o fundo. Município com produção residual quase desaparece.

---

## A causa raiz

`px.choropleth_map` só pinta as `locations` que você passa. Se você filtra `df[df["Producao"] > 0]` (recomendável, senão Plotly distribui a escala incluindo zeros), os não-produtores **somem** — mas o GeoJSON continua lá invisível, e o leitor não tem referência espacial.

É um problema de **engenharia de comunicação visual**, não de código.

---

## A solução: duas camadas

A ideia: separar **"existe nesse estado"** de **"tem o dado que estou plotando"**.

```
Camada 1 (fundo): TODOS os municípios em cinza-neutro
                  → define silhueta do estado
Camada 2 (topo):  Apenas produtores com escala Viridis
                  → comunica o dado
```

Implementação com `plotly.graph_objects.Choroplethmap` (não o `express`, porque precisamos sobrepor):

```python
import plotly.graph_objects as go

# Separa os dois grupos
df_prod = df[df["Producao"] > 0]
df_nao_prod = df[df["Producao"] == 0]

fig = go.Figure()

# CAMADA 1: silhueta cinza
fig.add_trace(go.Choroplethmap(
    geojson=geojson,
    locations=df_nao_prod["Municipio"],
    featureidkey="properties.name",
    z=[1] * len(df_nao_prod),                          # valor dummy
    colorscale=[[0, "#3a3f4f"], [1, "#3a3f4f"]],       # cor única
    showscale=False,                                   # sem barra de cor
    marker_line_color="rgba(255,255,255,0.5)",         # contorno branco translúcido
    marker_line_width=0.7,
    marker_opacity=0.85,
    hovertemplate="<b>%{location}</b><br>Sem produção<extra></extra>",
))

# CAMADA 2: produtores com Viridis
fig.add_trace(go.Choroplethmap(
    geojson=geojson,
    locations=df_prod["Municipio"],
    featureidkey="properties.name",
    z=df_prod["Producao"],
    colorscale="Viridis",
    marker_line_color="rgba(255,255,255,0.6)",
    marker_line_width=0.7,
    marker_opacity=0.85,
    hovertemplate="<b>%{location}</b><br>Produção: %{z:,.0f} t<extra></extra>",
))

fig.update_layout(
    map_style="carto-darkmatter",
    map_zoom=5.6,
    map_center={"lat": -10.9, "lon": -62.8},
)
```

Resultado: **silhueta clara do estado** com dados em Viridis sobrepostos. Quem está fora do estado some no fundo do `carto-darkmatter`. Quem está no estado mas não produz fica em cinza visível com contorno.

---

## Bônus: hover diferenciado

A ambiguidade não termina na cor. Hover também precisa diferenciar:

```python
# Não-produtor
hovertemplate="<b>{municipio}</b><br>Sem produção registrada"

# Produtor
hovertemplate="<b>{municipio}</b><br>Produção: {valor} t"
```

O leitor passa o mouse e **sabe imediatamente** se é "0 produção" ou "não cultiva essa cultura". São coisas diferentes.

---

## Bônus 2: escala humana no hover

Outro vacilo recorrente: hover mostrando `Valor (R$ mil): 468,235 R$ mil`.

Dois problemas:
1. Unidade duplicada (uma do label, outra do template)
2. 468 mil mil = **468 milhões** — mas o leitor lê "468 mil"

Solução: pré-formatar em Python antes de passar pro Plotly.

```python
def fmt_valor(val):
    if val >= 1_000_000:
        return f"R$ {val/1e6:,.2f} Bi"
    if val >= 1_000:
        return f"R$ {val/1e3:,.1f} Mi"
    return f"R$ {val:,.0f} mil"

customdata = [[m, fmt_valor(v)] for m, v in zip(df_prod["Municipio"], df_prod["Valor"])]

fig.add_trace(go.Choroplethmap(
    ...,
    customdata=customdata,
    hovertemplate="<b>%{customdata[0]}</b><br>Valor: %{customdata[1]}<extra></extra>",
))
```

Hover passa a mostrar `Valor: R$ 468,2 Mi` — legível em qualquer dispositivo.

---

## Por que isso é "engenharia de comunicação"

Mapa não serve para impressionar — serve para o leitor **fazer perguntas certas em segundos**. Se ele para para pensar "isso é dado ou é fora do estado?", você falhou na comunicação **antes** dele olhar para o número.

Os 30 segundos extras de código que essa solução pede pagam-se na primeira reunião que você apresentar o mapa.

---

## Quando NÃO aplicar

❌ **Se 100% dos municípios têm dado.** Não precisa de camada de silhueta.  
❌ **Se o mapa é country-level** (estados de um país). `carto-darkmatter` já mostra fronteiras nacionais.  
❌ **Quando você quer destacar a ausência de dado como insight** ("vazio aqui é informação, não ruído").

---

## Código completo aplicado

Repositório: **github.com/vnavarro87/lavouras-ro** → arquivo `app.py`, função do mapa.

Onde está aplicado:
- 4 culturas diferentes (soja, milho, café, cacau)
- Café e cacau têm muitos não-produtores → silhueta brilha mais
- Filtro de município destaca borda mais grossa quando selecionado

Licença AGPL-3.0.

---

## Conclusão

Mapas coropléticos são fáceis de fazer mal. A diferença entre um mapa "funcional" e um mapa "defensável" é se o leitor consegue distinguir, sem hesitar:

1. **O que é dentro do estado** vs. **fora**
2. **Sem dado** vs. **dado igual a zero**
3. **Valores no hover** sem ambiguidade de unidade

Três checklist items. Trinta linhas de código. Diferença de impressão profissional vs amadora.

---

**Vinicius Navarro**  
Trader de dólar (WDO/B3) · Análise de risco agrícola · Rondônia  
Estudando MBA em Data Science, IA & Analytics  
[LinkedIn / GitHub links — inserir quando publicar]

---

## Notas para Publicação

- [ ] Inserir screenshot **antes** (mapa só com produtores, municípios pretos confusos)
- [ ] Inserir screenshot **depois** (silhueta + Viridis sobreposto)
- [ ] Inserir GIF/screenshot do hover diferenciado
- [ ] Linkar repositório `lavouras-ro` no GitHub
- [ ] Cross-link com posts da série soja-milho-ro (este complementa o lado "visualização")
- [ ] Tags sugeridas: #python #streamlit #plotly #datavisualization #brasil #agro
