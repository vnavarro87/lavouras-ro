import streamlit as st
import pandas as pd
import plotly.express as px
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

fig_mapa = px.choropleth_mapbox(
    df, geojson=geojson, locations="Municipio", featureidkey="properties.name",
    color=col_mapa, color_continuous_scale="Viridis",
    mapbox_style="carto-darkmatter", zoom=zoom_atual, center=centro_atual,
    opacity=0.7, hover_name="Municipio",
    labels={col_mapa: metrica_mapa},
)
if mun_sel != "Rondônia (todos)":
    fig_mapa.update_traces(marker_line_width=2, marker_line_color="white")
fig_mapa.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor="rgba(0,0,0,0)",
    uirevision=f"{cultura_sel}-{mun_sel}",
)
st.plotly_chart(fig_mapa, use_container_width=True)

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
    )
    fig_prod.update_traces(marker_color="#00d26a")
    st.plotly_chart(fig_prod, use_container_width=True)

# Gráfico 2: Top 15 por Produtividade (colorido por acima/abaixo da média)
with col_r2:
    top15_eff = df_rank[df_rank[cfg["col_prod"]] > 0].nlargest(15, cfg["col_prod"]).sort_values(cfg["col_prod"])
    fig_eff = px.bar(
        top15_eff, x=cfg["col_prod"], y="Municipio", orientation="h",
        labels={cfg["col_prod"]: "Produtividade (kg/ha)", "Municipio": ""},
        title=f"Quem produz melhor (kg/ha) — {cultura_sel}",
        color="cor_prod",
        color_discrete_map="identity",
    )
    fig_eff.add_vline(
        x=media_prod, line_dash="dash", line_color="white",
        annotation_text=f"Média: {media_prod:,.0f} kg/ha",
        annotation_position="top right",
        annotation_font_color="white",
    )
    fig_eff.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        title_font_size=14,
        margin={"t": 40, "b": 0, "l": 0, "r": 0},
        showlegend=False,
    )
    st.plotly_chart(fig_eff, use_container_width=True)

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
