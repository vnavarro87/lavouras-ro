import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="Lavouras de Rondônia", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .disclaimer {
        background-color: #2b2f3e; color: #d0d4dc;
        padding: 10px 14px; border-radius: 6px;
        border-left: 3px solid #00d26a;
        font-size: 13px; margin-bottom: 16px;
    }
    .context-box {
        background-color: #1e2130; border-radius: 10px;
        padding: 14px 16px; border-left: 4px solid #00d26a;
        font-size: 14px; color: #d0d4dc; margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DAS CULTURAS ---
# Benchmark = produtividade média histórica de referência nacional para a cultura.
# Permite contextualizar se RO está acima/abaixo da referência brasileira.
# Fontes: CONAB Acompanhamento da Safra; IBGE-PAM nacional; Embrapa.
CULTURAS = {
    "Soja": {
        "col_qtd":   "Soja_Qtd_T",
        "col_valor": "Soja_Valor_Mil",
        "col_prod":  "Soja_Prod_KgHa",
        "col_area":  "Soja_AreaPlant_Ha",
        "benchmark_kgha": 3450,
        "benchmark_label": "Brasil (CONAB safra 2023/24)",
        "contexto": (
            "Principal lavoura temporária de Rondônia, com escoamento via Arco Norte "
            "(Porto Velho → Itacoatiara → Santarém). "
            "O Cone Sul (Vilhena, Cerejeiras, Chupinguaia, Corumbiara, Pimenteiras do Oeste) "
            "concentra a maior parte da produção e rivaliza em escala com municípios do Mato Grosso. "
            "Vale do Guaporé e Porto Velho têm expansão recente (BR-364 sentido Abunã). "
            "Toda a produção é commodity para exportação — preço CBOT (Chicago) é a referência. "
            "Para análise de risco com preço internacional e câmbio, ver projeto soja-milho-ro."
        ),
    },
    "Milho": {
        "col_qtd":   "Milho_Qtd_T",
        "col_valor": "Milho_Valor_Mil",
        "col_prod":  "Milho_Prod_KgHa",
        "col_area":  "Milho_AreaPlant_Ha",
        "benchmark_kgha": 5500,
        "benchmark_label": "Brasil 2ª safra (CONAB 2023/24)",
        "contexto": (
            "Predomina o sistema safrinha (2ª safra), semeado em fevereiro logo após a colheita da soja "
            "no mesmo campo. Cone Sul mecanizado tem produtividade de 4.500–6.000 kg/ha. "
            "Há também milho de 1ª safra em pequena escala na Zona da Mata e Vale do Guaporé "
            "(produtividade 1.500–3.000 kg/ha, agricultura familiar e silagem). "
            "Demanda doméstica forte (ração para frangos, suínos, gado confinado), parte é exportada via Arco Norte."
        ),
    },
    "Café": {
        "col_qtd":   "Cafe_Qtd_T",
        "col_valor": "Cafe_Valor_Mil",
        "col_prod":  "Cafe_Prod_KgHa",
        "col_area":  None,
        "benchmark_kgha": 2500,
        "benchmark_label": "Espírito Santo conilon (CONAB 2023)",
        "contexto": (
            "Rondônia é o **2º maior produtor brasileiro de Coffea canephora (conilon/robusta)**, "
            "atrás apenas do Espírito Santo. Não é o mesmo café arábica de MG/SP — é a espécie "
            "usada principalmente em blends para café solúvel e como base para espresso. "
            "Cacoal, Nova Brasilândia, São Miguel do Guaporé lideram em volume; "
            "Candeias do Jamari, Alvorada D'Oeste, Mirante da Serra lideram em produtividade "
            "(4.000+ kg/ha — topo nacional para conilon, com clonagem e manejo intensivo). "
            "Mercado: blends para indústria, exportação para Europa e Ásia, expansão em cafés finos certificados."
        ),
    },
    "Cacau": {
        "col_qtd":   "Cacau_Qtd_T",
        "col_valor": "Cacau_Valor_Mil",
        "col_prod":  "Cacau_Prod_KgHa",
        "col_area":  None,
        "benchmark_kgha": 700,
        "benchmark_label": "Brasil (CONAB 2023, estados produtores)",
        "contexto": (
            "Cacau (Theobroma cacao) é cultura amazônica nativa em expansão consolidada em RO desde os anos 2000. "
            "Diferente da Bahia (cabruca tradicional) e do Pará (extensivo), em Rondônia há nicho crescente "
            "de **cacau-fino certificado** (heirloom genetics, fermentação controlada) que abastece chocolatarias "
            "premium. Jaru, Ouro Preto do Oeste, Governador Jorge Teixeira e Machadinho D'Oeste concentram a produção. "
            "Produtividade ainda em consolidação (RO ~1.500 kg/ha vs. ideal global ~2.500 kg/ha), "
            "com espaço grande para ganho via genética clonal e manejo de sombra."
        ),
    },
}


@st.cache_data
def carregar_dados():
    pasta = os.path.dirname(__file__)
    df = pd.read_csv(os.path.join(pasta, "dados_agro_ro_master.csv"))
    for col in df.columns:
        if col != "Municipio":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    with open(os.path.join(pasta, "mapa_ro.json"), encoding="utf-8") as f:
        geojson = json.load(f)
    return df, geojson


df, geojson = carregar_dados()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Lavouras de RO")
    st.caption("Produção agrícola municipal — dados públicos do IBGE.")
    st.markdown("---")

    cultura_sel = st.selectbox("Cultura:", list(CULTURAS.keys()))
    cfg = CULTURAS[cultura_sel]

    st.markdown("---")

    municipios_lista = ["Rondônia (todos)"] + sorted(df["Municipio"].unique().tolist())
    mun_sel = st.selectbox("Município em foco:", municipios_lista)

    st.markdown("---")
    st.subheader("Fontes")
    st.caption("""
    - **PAM 2023** (lavoura temporária): tabela 1612
    - **PAM 2023** (lavoura permanente): tabela 1613
    - **Geometria:** Malha Municipal IBGE 2022
    - Coleta via API SIDRA — último período disponível
    """)
    st.caption("Veja `METODOLOGIA.md` para detalhes sobre tratamento de dados.")

# --- ZOOM POR MUNICÍPIO ---
zoom_atual = 5.6
centro_atual = {"lat": -10.9, "lon": -62.8}

if mun_sel != "Rondônia (todos)":
    for feature in geojson["features"]:
        if feature["properties"]["name"] == mun_sel:
            geom = feature["geometry"]
            pontos = []
            if geom["type"] == "Polygon":
                pontos = geom["coordinates"][0]
            elif geom["type"] == "MultiPolygon":
                for poli in geom["coordinates"]:
                    for anel in poli:
                        pontos.extend(anel)
            validos = [p for p in pontos if isinstance(p, list) and len(p) >= 2]
            if validos:
                centro_atual = {
                    "lat": sum(p[1] for p in validos) / len(validos),
                    "lon": sum(p[0] for p in validos) / len(validos),
                }
                zoom_atual = 8.5
            break

# --- HEADER ---
st.title("Lavouras de Rondônia")
st.markdown(
    '<div class="disclaimer">'
    "Visualização de dados públicos do IBGE (PAM 2023). "
    "Os números refletem o último ano fechado da Produção Agrícola Municipal — "
    "não é informação em tempo real."
    "</div>",
    unsafe_allow_html=True,
)

# --- CONTEXTO DA CULTURA ---
st.markdown(
    f'<div class="context-box"><b>{cultura_sel} em RO:</b> {cfg["contexto"]}</div>',
    unsafe_allow_html=True,
)

# --- KPIs ---
df_foco = df if mun_sel == "Rondônia (todos)" else df[df["Municipio"] == mun_sel]

producao  = df_foco[cfg["col_qtd"]].sum()
valor     = df_foco[cfg["col_valor"]].sum()
prod_cols = df[df[cfg["col_prod"]] > 0][cfg["col_prod"]]
prod_media = prod_cols.mean() if not prod_cols.empty else 0

kpi_cols = st.columns(4 if cfg["col_area"] else 3)

with kpi_cols[0]:
    st.metric("Produção total", f"{producao/1e3:,.1f} mil t" if producao >= 1e3 else f"{producao:,.0f} t")
with kpi_cols[1]:
    st.metric("Produtividade média", f"{prod_media:,.0f} kg/ha")
with kpi_cols[2]:
    st.metric("Valor da produção", f"R$ {valor/1e3:.1f} Mi" if valor >= 1e3 else f"R$ {valor:,.0f} mil")

if cfg["col_area"]:
    area = df_foco[cfg["col_area"]].sum()
    with kpi_cols[3]:
        st.metric("Área plantada", f"{area/1e3:,.1f} mil ha")

# Preço médio recebido — calculado direto do PAM (Valor R$ mil ÷ Quantidade t × 1000)
# Único caso onde IBGE permite estimar preço sem fonte externa: a divisão entre as
# duas variáveis publicadas dá o preço médio implícito daquela cultura no agregado.
if producao > 0:
    preco_medio_t = (valor * 1_000) / producao
    st.markdown(
        f'<div style="background:#1e2130;border-left:3px solid #00d26a;padding:8px 12px;'
        f'border-radius:4px;font-size:13px;color:#d0d4dc;margin:8px 0;">'
        f"Preço médio implícito recebido em "
        f"<b>{mun_sel if mun_sel != 'Rondônia (todos)' else 'Rondônia'}</b>: "
        f'<b style="color:#00d26a">R$ {preco_medio_t:,.0f}/t</b> '
        f"<span style='color:#9ca3af'>(Valor PAM ÷ Quantidade — referência IBGE, não preço spot)</span>"
        f'</div>',
        unsafe_allow_html=True,
    )

# Concentração geográfica como métrica de risco regional.
# Calculada apenas em modo "Rondônia (todos)" — não faz sentido para 1 município.
if mun_sel == "Rondônia (todos)" and producao > 0:
    df_conc = df[df[cfg["col_qtd"]] > 0].copy()
    n_municipios_prod = len(df_conc)
    df_conc_sorted = df_conc.sort_values(cfg["col_qtd"], ascending=False)
    top5 = df_conc_sorted.head(5)
    pct_top5 = top5[cfg["col_qtd"]].sum() / producao * 100
    pct_top1 = top5[cfg["col_qtd"]].iloc[0] / producao * 100 if len(top5) > 0 else 0
    top1_nome = top5["Municipio"].iloc[0] if len(top5) > 0 else "—"

    # Classificação qualitativa de concentração (baseada em índice tipo HHI simplificado)
    if pct_top5 >= 70:
        nivel = "<b style='color:#ff4b4b'>alta</b>"
        nivel_caption = "exposição concentrada — choque logístico ou climático em poucos municípios afeta toda a produção estadual"
    elif pct_top5 >= 50:
        nivel = "<b style='color:#ffbd45'>média</b>"
        nivel_caption = "concentração relevante — poucos municípios respondem por mais da metade do volume"
    else:
        nivel = "<b style='color:#00d26a'>diluída</b>"
        nivel_caption = "produção distribuída — risco geográfico baixo, mas pode indicar agricultura familiar dispersa"

    st.markdown(
        f'<div style="background:#1e2130;border-left:3px solid #ffbd45;padding:10px 14px;'
        f'border-radius:4px;font-size:13px;color:#d0d4dc;margin:8px 0;">'
        f'<b>Concentração geográfica:</b> top 5 municípios = '
        f'<b style="color:#ffbd45">{pct_top5:.1f}%</b> da produção estadual '
        f'(top 1 — {top1_nome} — sozinho responde por {pct_top1:.1f}%) · '
        f'concentração {nivel}<br>'
        f'<span style="color:#9ca3af">{nivel_caption}. '
        f'Total de {n_municipios_prod} municípios produtores em RO.</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- MAPA ---
st.subheader(f"Distribuição de {cultura_sel} por município")

opcoes_mapa = {"Quantidade (t)": cfg["col_qtd"], "Produtividade (kg/ha)": cfg["col_prod"], "Valor (R$)": cfg["col_valor"]}
metrica_mapa = st.radio("Métrica:", list(opcoes_mapa.keys()), horizontal=True)
col_mapa = opcoes_mapa[metrica_mapa]

# Hover: label curto (sem unidade entre parênteses) + valor pré-formatado em escala humana.
# Produção e Valor adaptam escala (mil/Mi); Produtividade mantém kg/ha (não acumula).
_label_curto = {
    "Quantidade (t)":         "Produção",
    "Produtividade (kg/ha)":  "Produtividade",
    "Valor (R$)":             "Valor",
}[metrica_mapa]


def _fmt_metrica(val, metrica):
    if metrica == "Quantidade (t)":
        if val >= 1_000_000:
            return f"{val/1e6:,.2f} Mi t"
        if val >= 1_000:
            return f"{val/1e3:,.1f} mil t"
        return f"{val:,.0f} t"
    if metrica == "Produtividade (kg/ha)":
        return f"{val:,.0f} kg/ha"
    if metrica == "Valor (R$)":
        # CSV armazena em R$ mil; converte conforme magnitude
        if val >= 1_000_000:
            return f"R$ {val/1e6:,.2f} Bi"  # mil × milhão = bilhão
        if val >= 1_000:
            return f"R$ {val/1e3:,.1f} Mi"  # mil × mil = milhão
        return f"R$ {val:,.0f} mil"
    return f"{val:,.0f}"


# Separa produtores e não-produtores da cultura selecionada
df_prod = df[df[col_mapa] > 0].copy()
df_nao_prod = df[df[col_mapa] == 0].copy()

# Camada 1: silhueta cinza de RO (todos os municípios sem produção)
fig_mapa = go.Figure()
if not df_nao_prod.empty:
    fig_mapa.add_trace(go.Choroplethmap(
        geojson=geojson,
        locations=df_nao_prod["Municipio"],
        featureidkey="properties.name",
        z=[1] * len(df_nao_prod),
        colorscale=[[0, "#3a3f4f"], [1, "#3a3f4f"]],
        showscale=False,
        marker_line_color="rgba(255,255,255,0.5)",
        marker_line_width=0.7,
        marker_opacity=0.85,
        customdata=df_nao_prod["Municipio"].apply(
            lambda m: f"<b>{m}</b><br>Sem produção registrada de {cultura_sel.lower()}"
        ),
        hovertemplate="%{customdata}<extra></extra>",
        name="",
    ))

# Camada 2: produtores com escala Viridis
if not df_prod.empty:
    _highlight = mun_sel if mun_sel != "Rondônia (todos)" else None
    _line_widths = [2.5 if m == _highlight else 0.7 for m in df_prod["Municipio"]]
    _line_colors = ["#ffffff" if m == _highlight else "rgba(255,255,255,0.6)"
                    for m in df_prod["Municipio"]]
    # customdata: [município, valor_formatado] — pré-formatado em PT-BR / escala humana
    _hover_customdata = [
        [m, _fmt_metrica(v, metrica_mapa)]
        for m, v in zip(df_prod["Municipio"], df_prod[col_mapa])
    ]
    fig_mapa.add_trace(go.Choroplethmap(
        geojson=geojson,
        locations=df_prod["Municipio"],
        featureidkey="properties.name",
        z=df_prod[col_mapa],
        colorscale="Viridis",
        marker_line_color=_line_colors,
        marker_line_width=_line_widths,
        marker_opacity=0.85,
        customdata=_hover_customdata,
        hovertemplate=(
            f"<b>%{{customdata[0]}}</b><br>{_label_curto}: %{{customdata[1]}}<extra></extra>"
        ),
        colorbar=dict(title=metrica_mapa),
        name="",
    ))

fig_mapa.update_layout(
    map_style="carto-darkmatter",
    map_zoom=zoom_atual,
    map_center=centro_atual,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor="rgba(0,0,0,0)",
    uirevision=f"{cultura_sel}-{mun_sel}",
    hoverlabel=dict(bgcolor="#1e2130", bordercolor="#00d26a", font=dict(color="#ffffff")),
)
st.plotly_chart(fig_mapa, width='stretch', config={'displayModeBar': False})

# Legenda visual + transparência sobre limitação do PAM
st.markdown(
    f'<div style="background:#1e2130;padding:8px 12px;border-radius:4px;'
    f'font-size:12px;color:#9ca3af;margin-top:6px;">'
    f'<b style="color:#d0d4dc">Como ler o mapa:</b> '
    f'<span style="color:#3a3f4f;background:#3a3f4f;padding:0 6px;border-radius:2px;">▮▮</span> '
    f'<span style="color:#d0d4dc">cinza</span> = sem produção registrada de {cultura_sel.lower()} '
    f'<i>ou sob sigilo estatístico do IBGE</i> (municípios com poucos produtores têm dados suprimidos para preservar identidade). '
    f'<span style="color:#440154;background:#440154;padding:0 6px;border-radius:2px;">▮▮</span> '
    f'<span style="color:#d0d4dc">roxo</span> = produção baixa · '
    f'<span style="color:#fde725;background:#fde725;padding:0 6px;border-radius:2px;">▮▮</span> '
    f'<span style="color:#d0d4dc">amarelo</span> = produção alta. '
    f'Município com borda branca grossa = selecionado na sidebar.'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# --- VOLUME × PRODUTIVIDADE ---
st.subheader("Volume × Produtividade")

df_rank = df[df[cfg["col_qtd"]] > 0].copy()
df_rank_prod = df_rank[df_rank[cfg["col_prod"]] > 0].copy()

# Filtro de relevância para ranking de produtividade: produção residual (< 5% da
# produção total estadual da cultura, com piso de 50 t) é excluída do ranking
# de eficiência. Sem isso, município com 2 t e 2.000 kg/ha aparece como #1
# em produtividade, distorcendo a leitura.
total_estadual = df_rank[cfg["col_qtd"]].sum()
piso_relevancia = max(50.0, total_estadual * 0.005)  # 0,5% do total ou 50 t
df_rank_eff = df_rank_prod[df_rank_prod[cfg["col_qtd"]] >= piso_relevancia].copy()
n_excluidos = len(df_rank_prod) - len(df_rank_eff)

media_prod = df_rank_eff[cfg["col_prod"]].mean() if not df_rank_eff.empty else 0
df_rank["cor_prod"] = df_rank[cfg["col_prod"]].apply(
    lambda v: "#00d26a" if v >= media_prod else "#6b7280"
)
df_rank_eff["cor_prod"] = df_rank_eff[cfg["col_prod"]].apply(
    lambda v: "#00d26a" if v >= media_prod else "#6b7280"
)

col_r1, col_r2 = st.columns(2)

# Gráfico 1: Quem mais produz (volume) — todos os produtores (não só top 15)
with col_r1:
    df_top_prod = df_rank.sort_values(cfg["col_qtd"])
    fig_prod = px.bar(
        df_top_prod, x=cfg["col_qtd"], y="Municipio", orientation="h",
        labels={cfg["col_qtd"]: "Produção (t)", "Municipio": ""},
        title=f"Quem mais produz — {cultura_sel} ({len(df_top_prod)} municípios)",
        color_discrete_sequence=["#00d26a"],
    )
    fig_prod.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        title_font_size=14,
        margin={"t": 40, "b": 0, "l": 0, "r": 0},
        showlegend=False,
        hoverlabel=dict(bgcolor="#1e2130", bordercolor="#00d26a", font=dict(color="#ffffff")),
        height=max(380, len(df_top_prod) * 22),
    )
    fig_prod.update_traces(
        marker_color=df_top_prod["cor_prod"].tolist(),
        hovertemplate="<b>%{y}</b><br>Produção: %{x:,.0f} t<extra></extra>",
    )
    st.plotly_chart(fig_prod, width='stretch', config={'displayModeBar': False})

# Gráfico 2: Quem produz melhor (kg/ha) — apenas com produção relevante
with col_r2:
    df_top_eff = df_rank_eff.sort_values(cfg["col_prod"])
    n_acima = int((df_top_eff[cfg["col_prod"]] >= media_prod).sum())
    n_total = len(df_top_eff)

    aviso_filtro = (
        f" · {n_excluidos} excluído(s) por produção &lt; {piso_relevancia:,.0f} t"
        if n_excluidos > 0 else ""
    )
    # Benchmark nacional: contextualiza se média estadual está acima/abaixo da referência BR
    benchmark = cfg.get("benchmark_kgha")
    benchmark_label = cfg.get("benchmark_label", "")
    if benchmark:
        delta_pct = (media_prod / benchmark - 1) * 100
        cor_delta = "#00d26a" if delta_pct >= 0 else "#ff4b4b"
        sinal = "+" if delta_pct >= 0 else ""
        bench_html = (
            f' · vs <b>{benchmark:,.0f} kg/ha</b> ({benchmark_label}): '
            f'<span style="color:{cor_delta}">{sinal}{delta_pct:.1f}%</span>'
        )
    else:
        bench_html = ""
    st.markdown(
        f'<div style="background:#1e2130;border-left:3px solid #ffbd45;padding:8px 12px;'
        f'border-radius:4px;font-size:13px;color:#d0d4dc;margin-bottom:6px;">'
        f'Média RO: <b style="color:#ffbd45">{media_prod:,.0f} kg/ha</b>'
        f'{bench_html}<br>'
        f'<span style="color:#00d26a">{n_acima}</span> acima da média estadual · '
        f'<span style="color:#9ca3af">{n_total - n_acima}</span> abaixo'
        f'{aviso_filtro}'
        f'</div>',
        unsafe_allow_html=True,
    )

    fig_eff = px.bar(
        df_top_eff, x=cfg["col_prod"], y="Municipio", orientation="h",
        labels={cfg["col_prod"]: "Produtividade (kg/ha)", "Municipio": ""},
        title=f"Quem produz melhor (kg/ha) — {cultura_sel} ({n_total} municípios)",
        color="cor_prod",
        color_discrete_map="identity",
    )
    fig_eff.add_vline(
        x=media_prod, line_color="#ffbd45", line_width=1.5, opacity=0.7,
    )
    fig_eff.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        title_font_size=14,
        margin={"t": 40, "b": 0, "l": 0, "r": 0},
        showlegend=False,
        hoverlabel=dict(bgcolor="#1e2130", bordercolor="#00d26a", font=dict(color="#ffffff")),
        height=max(380, n_total * 22),
    )
    fig_eff.update_traces(
        hovertemplate="<b>%{y}</b><br>Produtividade: %{x:,.0f} kg/ha<extra></extra>",
    )
    st.plotly_chart(fig_eff, width='stretch', config={'displayModeBar': False})

st.caption(
    "Volume alto não significa eficiência alta — os dois rankings juntos mostram quem produz muito "
    "e quem produz bem. Verde = acima da média estadual de produtividade. "
    f"Para evitar distorção do ranking de produtividade por município com produção residual, "
    f"o corte de relevância é {piso_relevancia:,.0f} t (0,5% da produção total estadual ou 50 t, o maior)."
)

st.markdown("---")

# --- RODAPÉ ---
st.caption(
    "Dados: IBGE / PAM 2023 (API SIDRA). "
    "Limitações: dados anuais; valores em reais correntes do ano de referência; "
    "células suprimidas por sigilo estatístico tratadas como zero. "
    "Veja METODOLOGIA.md para detalhes."
)
