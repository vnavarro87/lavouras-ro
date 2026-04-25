import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Mapa da Soja em Rondônia",
    layout="wide"
)

# --- ESTILO ---
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
    </style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_dados():
    pasta = os.path.dirname(__file__)
    df = pd.read_csv(os.path.join(pasta, "dados_agro_ro_master.csv"))
    for col in df.columns:
        if col != "Municipio":
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    with open(os.path.join(pasta, "mapa_ro.json"), encoding='utf-8') as f:
        geojson = json.load(f)
    return df, geojson

df, geojson = carregar_dados()

# Apenas colunas de soja são usadas neste projeto
df = df[["Municipio", "Soja_Qtd_T", "Soja_Valor_Mil",
         "Soja_Prod_KgHa", "Soja_AreaPlant_Ha"]].copy()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Mapa da Soja | RO")
    st.caption("Produção municipal a partir de dados públicos do IBGE.")
    st.markdown("---")

    municipios_lista = ["Rondônia (todos)"] + sorted(df['Municipio'].unique().tolist())
    mun_selecionado = st.selectbox("Município em foco:", municipios_lista)

    st.markdown("---")
    st.subheader("Fontes")
    st.caption("""
    - **Produção, área e valor:** IBGE / PAM 2023 (tabela 1612)
    - **Geometria:** Malha Municipal IBGE 2022
    - **Coleta:** API SIDRA, último período disponível
    """)
    st.caption("Código aberto no GitHub. Veja `METODOLOGIA.md` para detalhes.")

# --- HEADER ---
st.title("Mapa da Soja em Rondônia")
st.markdown(
    '<div class="disclaimer">'
    'Visualização de dados públicos do IBGE (PAM 2023). '
    'Os números refletem o último ano fechado da Produção Agrícola Municipal — '
    'não é informação em tempo real.'
    '</div>',
    unsafe_allow_html=True
)

# --- LÓGICA DE FOCO REGIONAL ---
zoom_atual = 5.6
centro_atual = {"lat": -10.9, "lon": -62.8}

if mun_selecionado != "Rondônia (todos)":
    for feature in geojson['features']:
        if feature['properties']['name'] == mun_selecionado:
            geom = feature['geometry']
            pontos = []
            if geom['type'] == 'Polygon':
                pontos = geom['coordinates'][0]
            elif geom['type'] == 'MultiPolygon':
                for poli in geom['coordinates']:
                    for anel in poli:
                        pontos.extend(anel)
            pontos_validos = [p for p in pontos if isinstance(p, list) and len(p) >= 2]
            if pontos_validos:
                lon = sum(p[0] for p in pontos_validos) / len(pontos_validos)
                lat = sum(p[1] for p in pontos_validos) / len(pontos_validos)
                centro_atual = {"lat": lat, "lon": lon}
                zoom_atual = 8.5
            break

# --- KPIs ---
df_foco = df if mun_selecionado == "Rondônia (todos)" else df[df['Municipio'] == mun_selecionado]

producao_total = df_foco['Soja_Qtd_T'].sum()
area_total = df_foco['Soja_AreaPlant_Ha'].sum()
valor_total = df_foco['Soja_Valor_Mil'].sum()
prod_media = (producao_total * 1000 / area_total) if area_total > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Produção", f"{producao_total/1e6:.2f} Mi t" if producao_total >= 1e6 else f"{producao_total:,.0f} t")
with c2:
    st.metric("Área Plantada", f"{area_total/1e3:,.1f} mil ha")
with c3:
    st.metric("Produtividade Média", f"{prod_media:,.0f} kg/ha")
with c4:
    st.metric("Valor da Produção", f"R$ {valor_total/1e3:.1f} Mi" if valor_total >= 1e3 else f"R$ {valor_total:,.0f} mil")

st.markdown("---")

# --- SEÇÃO 1: MAPA ---
st.subheader("Distribuição da produção por município")

metrica_mapa = st.radio(
    "Métrica do mapa:",
    ["Quantidade (t)", "Produtividade (kg/ha)", "Área plantada (ha)"],
    horizontal=True
)
mapa_col = {
    "Quantidade (t)": "Soja_Qtd_T",
    "Produtividade (kg/ha)": "Soja_Prod_KgHa",
    "Área plantada (ha)": "Soja_AreaPlant_Ha"
}[metrica_mapa]

fig_mapa = px.choropleth_mapbox(
    df, geojson=geojson, locations="Municipio", featureidkey="properties.name",
    color=mapa_col, color_continuous_scale="Viridis",
    mapbox_style="carto-darkmatter", zoom=zoom_atual, center=centro_atual,
    opacity=0.7, hover_name="Municipio",
    labels={mapa_col: metrica_mapa}
)
if mun_selecionado != "Rondônia (todos)":
    fig_mapa.update_traces(marker_line_width=2, marker_line_color="white")
fig_mapa.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor='rgba(0,0,0,0)',
    uirevision=mun_selecionado
)
st.plotly_chart(fig_mapa, use_container_width=True)

st.markdown("---")

# --- SEÇÃO 2: RANKINGS E PERFORMANCE ---
col_r, col_s = st.columns([1, 2])

with col_r:
    st.subheader("Top 10 produtores")
    top10 = df.nlargest(10, "Soja_Qtd_T")[["Municipio", "Soja_Qtd_T"]].copy()
    top10.columns = ["Município", "Produção (t)"]
    top10["Produção (t)"] = top10["Produção (t)"].map(lambda v: f"{v:,.0f}")
    st.dataframe(top10, hide_index=True, use_container_width=True)

with col_s:
    st.subheader("Área x Produtividade")
    df_scatter = df[df["Soja_AreaPlant_Ha"] > 0].copy()
    media_prod = df_scatter["Soja_Prod_KgHa"].mean()

    fig_scatter = px.scatter(
        df_scatter,
        x="Soja_AreaPlant_Ha", y="Soja_Prod_KgHa",
        size="Soja_Qtd_T", hover_name="Municipio",
        labels={
            "Soja_AreaPlant_Ha": "Área plantada (ha)",
            "Soja_Prod_KgHa": "Produtividade (kg/ha)"
        },
        color_discrete_sequence=["#00d26a"]
    )
    fig_scatter.add_hline(
        y=media_prod, line_dash="dash", line_color="white",
        annotation_text=f"Média estadual: {media_prod:,.0f} kg/ha",
        annotation_position="top right"
    )
    fig_scatter.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.caption(
        "Cada bolha é um município. Tamanho representa a produção total. "
        "Municípios acima da linha tracejada têm produtividade superior à média estadual."
    )

st.markdown("---")

# --- RODAPÉ ---
st.caption(
    "Dados: IBGE / PAM 2023 (API SIDRA). "
    "Limitações conhecidas: dados anuais, sem desagregação intra-anual; "
    "valores monetários em reais correntes do ano de referência. "
    "Veja `METODOLOGIA.md` para o tratamento aplicado a dados ausentes e suprimidos."
)
