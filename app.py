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
CULTURAS = {
    "Soja": {
        "col_qtd":   "Soja_Qtd_T",
        "col_valor": "Soja_Valor_Mil",
        "col_prod":  "Soja_Prod_KgHa",
        "col_area":  "Soja_AreaPlant_Ha",
        "contexto": (
            "Principal lavoura temporária de Rondônia. "
            "O Cone Sul do estado — Vilhena, Cerejeiras e Chupinguaia — "
            "concentra a maior parte da produção e rivaliza em escala com municípios do Mato Grosso."
        ),
    },
    "Milho": {
        "col_qtd":   "Milho_Qtd_T",
        "col_valor": "Milho_Valor_Mil",
        "col_prod":  "Milho_Prod_KgHa",
        "col_area":  "Milho_AreaPlant_Ha",
        "contexto": (
            "Cultivado principalmente em sistema safrinha, logo após a colheita da soja. "
            "A produtividade média de RO supera 4.000 kg/ha, "
            "resultado da adoção de tecnologia no Cone Sul e na região de Ariquemes."
        ),
    },
    "Café": {
        "col_qtd":   "Cafe_Qtd_T",
        "col_valor": "Cafe_Valor_Mil",
        "col_prod":  "Cafe_Prod_KgHa",
        "col_area":  None,
        "contexto": (
            "Rondônia é um dos maiores produtores de Coffea canephora (robusta/conilon) do Brasil. "
            "Cacoal, São Miguel do Guaporé e Alta Floresta D'Oeste lideram, "
            "com produtividade acima da média nacional para a espécie."
        ),
    },
    "Cacau": {
        "col_qtd":   "Cacau_Qtd_T",
        "col_valor": "Cacau_Valor_Mil",
        "col_prod":  "Cacau_Prod_KgHa",
        "col_area":  None,
        "contexto": (
            "Cultura em expansão em RO, com destaque para o nicho de chocolate fino. "
            "Jaru é o maior produtor estadual com produtividade bem acima da média, "
            "seguida por municípios do Vale do Jamari."
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

st.markdown("---")

# --- MAPA ---
st.subheader(f"Distribuição de {cultura_sel} por município")

opcoes_mapa = {"Quantidade (t)": cfg["col_qtd"], "Produtividade (kg/ha)": cfg["col_prod"], "Valor (R$ mil)": cfg["col_valor"]}
metrica_mapa = st.radio("Métrica:", list(opcoes_mapa.keys()), horizontal=True)
col_mapa = opcoes_mapa[metrica_mapa]

# Hover: label curto (sem unidade entre parênteses) + valor pré-formatado em escala humana.
# Produção e Valor adaptam escala (mil/Mi); Produtividade mantém kg/ha (não acumula).
_label_curto = {
    "Quantidade (t)":         "Produção",
    "Produtividade (kg/ha)":  "Produtividade",
    "Valor (R$ mil)":         "Valor",
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
    if metrica == "Valor (R$ mil)":
        # CSV vem em R$ mil; converte conforme magnitude
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

st.markdown("---")

# --- RANKINGS ---
st.subheader("Análise de Performance")
col_r1, col_r2 = st.columns(2)

df_rank = df[df[cfg["col_qtd"]] > 0].copy()
media_prod = df[df[cfg["col_prod"]] > 0][cfg["col_prod"]].mean()
df_rank["cor_prod"] = df_rank[cfg["col_prod"]].apply(
    lambda v: "#00d26a" if v >= media_prod else "#6b7280"
)

# Gráfico 1: Top 15 por Produção
with col_r1:
    top15_prod = df_rank.nlargest(15, cfg["col_qtd"]).sort_values(cfg["col_qtd"])
    fig_prod = px.bar(
        top15_prod, x=cfg["col_qtd"], y="Municipio", orientation="h",
        labels={cfg["col_qtd"]: "Produção (t)", "Municipio": ""},
        title=f"Quem mais produz — {cultura_sel}",
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
    )
    fig_prod.update_traces(
        marker_color=top15_prod["cor_prod"].tolist(),
        hovertemplate="<b>%{y}</b><br>Produção: %{x:,.0f} t<extra></extra>",
    )
    st.plotly_chart(fig_prod, width='stretch', config={'displayModeBar': False})

# Gráfico 2: Todos os municípios por Produtividade (colorido por acima/abaixo da média)
with col_r2:
    top15_eff = df_rank[df_rank[cfg["col_prod"]] > 0].sort_values(cfg["col_prod"])
    n_acima = int((top15_eff[cfg["col_prod"]] >= media_prod).sum())
    n_total = len(top15_eff)

    # Indicador visual da média (chip discreto acima do gráfico — substitui linha vertical feia)
    st.markdown(
        f'<div style="background:#1e2130;border-left:3px solid #ffbd45;padding:8px 12px;'
        f'border-radius:4px;font-size:13px;color:#d0d4dc;margin-bottom:6px;">'
        f'Média estadual: <b style="color:#ffbd45">{media_prod:,.0f} kg/ha</b> · '
        f'<span style="color:#00d26a">{n_acima}</span> acima · '
        f'<span style="color:#9ca3af">{n_total - n_acima}</span> abaixo'
        f'</div>',
        unsafe_allow_html=True,
    )

    fig_eff = px.bar(
        top15_eff, x=cfg["col_prod"], y="Municipio", orientation="h",
        labels={cfg["col_prod"]: "Produtividade (kg/ha)", "Municipio": ""},
        title=f"Quem produz melhor (kg/ha) — {cultura_sel}",
        color="cor_prod",
        color_discrete_map="identity",
    )
    # Linha de referência sutil (sólida fina amarela, sem annotation embutida — está no chip acima)
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
    )
    fig_eff.update_traces(
        hovertemplate="<b>%{y}</b><br>Produtividade: %{x:,.0f} kg/ha<extra></extra>",
    )
    st.plotly_chart(fig_eff, width='stretch', config={'displayModeBar': False})

st.caption(
    "Volume alto não significa eficiência alta — os dois rankings juntos mostram quem produz muito "
    "e quem produz bem. Verde = acima da média estadual de produtividade."
)

st.markdown("---")

# --- RODAPÉ ---
st.caption(
    "Dados: IBGE / PAM 2023 (API SIDRA). "
    "Limitações: dados anuais; valores em reais correntes do ano de referência; "
    "células suprimidas por sigilo estatístico tratadas como zero. "
    "Veja METODOLOGIA.md para detalhes."
)
