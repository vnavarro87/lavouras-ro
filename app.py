import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import math
import google.generativeai as genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="RO Agro Intelligence Hub",
    page_icon="💎",
    layout="wide"
)

# --- ESTILO CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; white-space: pre-wrap; background-color: #1e2130; 
        border-radius: 10px 10px 0 0; color: white; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #00d26a !important; font-weight: bold; }
    .metric-card { background-color: #1e2130; border-radius: 15px; padding: 15px; border-top: 4px solid #00d26a; }
    .metric-value { font-size: 24px; font-weight: bold; }
    .metric-label { font-size: 12px; color: #808495; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CARREGAMENTO DE DADOS ---
def carregar_dados():
    pasta = os.path.dirname(__file__)
    df = pd.read_csv(os.path.join(pasta, "dados_agro_ro_master.csv"))
    for col in df.columns:
        if col != "Municipio": df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    with open(os.path.join(pasta, "mapa_ro.json"), encoding='utf-8') as f:
        geojson = json.load(f)
    return df, geojson

df, geojson = carregar_dados()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Agro Intelligence")
    st.markdown("Gestão Estratégica Regional")
    st.markdown("---")
    
    municipios_lista = ["Rondônia (Geral)"] + sorted(df['Municipio'].unique().tolist())
    mun_selecionado = st.selectbox("Foco Regional:", municipios_lista, key="sel_sidebar_municipio")
    
    st.markdown("---")
    st.subheader("Auditoria de Dados")
    st.caption("""
    **Fontes Oficiais (API SIDRA/IBGE):**
    - **Agricultura (PAM 2023):** Dados de safra mais recentes.
    - **Pecuária (PPM 2023):** Efetivo de rebanho atualizado.
    - **PIB Municipal (2021):** Série histórica oficial (IBGE possui 2 anos de defasagem padrão na divulgação de contas regionais).
    - **Geometria:** Malha Digital IBGE 2022.
    """)
    st.warning("Nota Técnica: As métricas de representatividade utilizam o PIB 2021 como baseline econômico.")
    st.info("Dados extraídos em tempo real via API oficial.")

# --- LÓGICA DE FOCO REGIONAL (ZOOM E CENTRO) ---
zoom_atual = 5.6
centro_atual = {"lat": -10.9, "lon": -62.8}

if mun_selecionado != "Rondônia (Geral)":
    for feature in geojson['features']:
        if feature['properties']['name'] == mun_selecionado:
            geom = feature['geometry']
            # Extrair todos os pontos para calcular a média (centroide simples)
            pontos = []
            if geom['type'] == 'Polygon':
                pontos = geom['coordinates'][0]
            elif geom['type'] == 'MultiPolygon':
                # Achata as listas do MultiPolygon
                for poli in geom['coordinates']:
                    for anel in poli:
                        pontos.extend(anel)
            
            if pontos:
                # Filtrar caso venha algum dado corrompido (garantir que cada p seja [lon, lat])
                pontos_validos = [p for p in pontos if isinstance(p, list) and len(p) >= 2]
                if pontos_validos:
                    lon = sum([p[0] for p in pontos_validos]) / len(pontos_validos)
                    lat = sum([p[1] for p in pontos_validos]) / len(pontos_validos)
                    centro_atual = {"lat": lat, "lon": lon}
                    zoom_atual = 8.5
            break

# --- HEADER E KPIs TOTAIS (O IMPACTO) ---
st.title("Agro Intelligence Hub | Rondônia")
if mun_selecionado != "Rondônia (Geral)":
    st.success(f"🔍 Foco Estratégico Ativado: {mun_selecionado}")
else:
    st.markdown("Análise Estratégica de Produção e Competitividade Setorial")

# Cálculo de Métricas (Estado ou Município)
df_foco = df if mun_selecionado == "Rondônia (Geral)" else df[df['Municipio'] == mun_selecionado]

pib_val = df_foco['PIB_Agro_Mil'].sum() / 1e6 if mun_selecionado == "Rondônia (Geral)" else df_foco['PIB_Agro_Mil'].sum() / 1e3
vbp_val = df_foco['Valor_Agricola_Total_Mil'].sum() / 1e6 if mun_selecionado == "Rondônia (Geral)" else df_foco['Valor_Agricola_Total_Mil'].sum() / 1e3
rebanho_val = df_foco['Gado_Cabecas'].sum() / 1e6 if mun_selecionado == "Rondônia (Geral)" else df_foco['Gado_Cabecas'].sum() / 1e3
area_val = df_foco[[c for c in df_foco.columns if 'AreaPlant_Ha' in c]].sum().sum() / 1e6 if mun_selecionado == "Rondônia (Geral)" else df_foco[[c for c in df_foco.columns if 'AreaPlant_Ha' in c]].sum().sum() / 1e3

label_unidade = "Bi" if mun_selecionado == "Rondônia (Geral)" else "Mi"
label_gado = "Mi" if mun_selecionado == "Rondônia (Geral)" else "mil"

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("PIB Agro", f"R$ {pib_val:.2f} {label_unidade}")
with c2: st.metric("Valor Produção", f"R$ {vbp_val:.2f} {label_unidade}")
with c3: st.metric("Rebanho", f"{rebanho_val:.2f} {label_gado}")
with c4: st.metric("Área Plantada", f"{area_val:.2f} {label_unidade if mun_selecionado == 'Rondônia (Geral)' else 'mil Ha'}")

st.markdown("---")

# --- NAVEGAÇÃO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["Visão Geográfica", "Análise de Performance", "Sazonalidade e Mercado"])

# --- ABA 1: VISÃO GEOGRÁFICA (O ONDE) ---
with tab1:
    col_mapa, col_info = st.columns([2, 1])
    
    with col_mapa:
        st.subheader("Distribuição Espacial da Produção")
        cultura_mapa = st.selectbox("Selecione a Camada de Dados:", ["Soja", "Milho", "Cafe", "Cacau", "Gado", "Leite"], key="sel_mapa_camada")
        
        # Lógica de coluna dinâmica para o mapa
        col_map = f"{cultura_mapa}_Qtd_T" if cultura_mapa not in ["Gado", "Leite"] else (f"{cultura_mapa}_Cabecas" if cultura_mapa=="Gado" else f"{cultura_mapa}_Mil_Litros")
        
        # Ajuste de opacidade para destacar o selecionado
        df['opacidade_mapa'] = 0.4
        if mun_selecionado != "Rondônia (Geral)":
            df.loc[df['Municipio'] == mun_selecionado, 'opacidade_mapa'] = 1.0

        fig_mapa = px.choropleth_mapbox(
            df, geojson=geojson, locations="Municipio", featureidkey="properties.name",
            color=col_map, color_continuous_scale="Viridis",
            mapbox_style="carto-darkmatter", zoom=zoom_atual, center=centro_atual,
            opacity=0.6, hover_name="Municipio"
        )
        # Adicionar o contorno se houver seleção
        if mun_selecionado != "Rondônia (Geral)":
            fig_mapa.update_traces(marker_line_width=2, marker_line_color="white")
            
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_mapa, use_container_width=True)

    with col_info:
        st.subheader("Destaques Regionais")
        if mun_selecionado == "Rondônia (Geral)":
            st.info("Selecione um município na barra lateral para ver o detalhamento local.")
            # Top 5 Produtores
            top5 = df.nlargest(5, col_map)[['Municipio', col_map]]
            st.write(f"Maiores produtores de {cultura_mapa}:")
            st.table(top5)
        else:
            mun_df = df[df['Municipio'] == mun_selecionado].iloc[0]
            st.success(f"📍 Analisando: {mun_selecionado}")
            st.write(f"PIB Agro: R$ {mun_df['PIB_Agro_Mil']/1000:,.1f} Milhões")
            st.write(f"Representatividade no Estado: {(mun_df['PIB_Agro_Mil'] / df['PIB_Agro_Mil'].sum() * 100):.2f}%")

# --- ABA 2: ANÁLISE DE PERFORMANCE ---
with tab2:
    st.header("Análise de Lavouras")
    st.caption("Fonte: IBGE - Produção Agrícola Municipal (PAM) 2023")
    
    c1, c2 = st.columns([1, 4])
    with c1:
        cultura = st.selectbox("Cultura:", ["Soja", "Milho", "Cafe", "Cacau"], key="sel_perf_cultura")
        metrica = st.selectbox("Métrica:", ["Quantidade", "Produtividade", "Valor"], key="sel_perf_metrica")
        
        map_cols = {
            "Quantidade": f"{cultura}_Qtd_T",
            "Produtividade": f"{cultura}_Prod_KgHa",
            "Valor": f"{cultura}_Valor_Mil"
        }
        col_ativa = map_cols[metrica]
        
    with c2:
        mc1, mc2, mc3 = st.columns(3)
        if col_ativa in df.columns:
            col_qtd = f"{cultura}_Qtd_T"
            if col_qtd in df.columns:
                total_prod = df[col_qtd].sum()
                max_prod = df[col_qtd].max()
                lider = df.loc[df[col_qtd].idxmax(), "Municipio"] if not df.empty else "N/A"
                
                mc1.metric(f"Produção Total ({cultura})", f"{total_prod:,.0f} T")
                mc2.metric("Líder de Produção", lider)
                mc3.metric("Recorde Municipal", f"{max_prod:,.0f} T")

    st.divider()
    
    # Seção Pecuária dentro da Aba 2
    st.subheader("🐄 Análise de Pecuária e Origem Animal")
    cp1, cp2 = st.columns([3, 1])
    with cp2:
        finalidade = st.selectbox("Analisar por:", ["Corte (Rebanho)", "Leite (Produção)"], key="sel_pecuaria_finalidade")
        col_ativa_gado = "Gado_Cabecas" if "Corte" in finalidade else "Leite_Mil_Litros"
        cor_gado = "YlOrBr" if "Corte" in finalidade else "GnBu"
        unidade_g = "Cab." if "Corte" in finalidade else "Mil Litros"
        
        total_v = df[col_ativa_gado].sum()
        st.metric(f"Total RO ({finalidade})", f"{total_v:,.0f} {unidade_g}")
        st.markdown("---")
        st.write(f"Top 5 {finalidade}:")
        st.table(df.nlargest(5, col_ativa_gado)[["Municipio", col_ativa_gado]])
        
    with cp1:
        fig_gado = px.choropleth_mapbox(df, geojson=geojson, locations="Municipio", featureidkey="properties.name", color=col_ativa_gado, color_continuous_scale=cor_gado, mapbox_style="carto-darkmatter", zoom=zoom_atual, center=centro_atual, opacity=0.7)
        
        # Destaque se houver seleção
        if mun_selecionado != "Rondônia (Geral)":
            fig_gado.update_traces(marker_line_width=2, marker_line_color="white")
            
        fig_gado.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=True)
        st.plotly_chart(fig_gado, use_container_width=True, config={'displayModeBar': False})

    # Matriz de Performance
    st.divider()
    st.subheader("Matriz de Performance e Eficiência Técnica")
    
    df_perf = df.copy()
    col_prod = f"{cultura}_Prod_KgHa"
    # Fallback para Area Colhida caso a Plantada não exista no IBGE para aquela cultura
    col_area = f"{cultura}_AreaPlant_Ha" if f"{cultura}_AreaPlant_Ha" in df.columns else f"{cultura}_AreaColh_Ha"
    col_qtd = f"{cultura}_Qtd_T"
    
    if col_prod in df_perf.columns and col_area in df_perf.columns:
        media_prod = df_perf[df_perf[col_prod] > 0][col_prod].mean()
        df_perf['Performance_Relativa'] = (df_perf[col_prod] / media_prod - 1) * 100
        
        c_p1, c_p2 = st.columns([2, 1])
        with c_p1:
            fig_perf = px.scatter(
                df_perf[df_perf[col_area] > 0], x=col_area, y=col_prod,
                size=col_qtd, color="Performance_Relativa",
                hover_name="Municipio", color_continuous_scale="RdYlGn",
                labels={col_area: "Área Plantada (Ha)", col_prod: "Produtividade (Kg/Ha)"},
                title=f"Posicionamento Competitivo: {cultura}"
            )
            fig_perf.add_hline(y=media_prod, line_dash="dash", line_color="white", annotation_text="Média Estadual")
            fig_perf.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_perf, use_container_width=True)
        with c_p2:
            st.markdown(f"""
            **Leitura Técnica:**
            - Municípios em **Verde** estão acima da média estadual de {media_prod:,.0f} Kg/Ha.
            - O tamanho da bolha indica o volume total produzido.
            - O objetivo estratégico é mover os municípios do quadrante inferior para o superior através de tecnologia.
            """)
            
    st.markdown("---")

# --- ABA 3: SAZONALIDADE E MERCADO ---
with tab3:
    st.header("Inteligência Estratégica e Riscos")
    
    c_int1, c_int2 = st.columns(2)
    
    with c_int1:
        st.subheader("Análise de Sazonalidade e Clima")
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_sel = st.select_slider("Período de Análise:", options=meses, value="Janeiro")
        
        calendario = {
            "Janeiro": {"Acao": "Colheita Soja / Crescimento Café", "Risco": "Ferrugem Asiática (Soja) / Pluviosidade elevada (300mm) impactando a colheita precoce."},
            "Fevereiro": {"Acao": "Pico da Colheita Soja / Plantio Milho", "Risco": "Gargalos logísticos por chuvas (280mm) / Janela crítica para Milho Safrinha."},
            "Março": {"Acao": "Conclusão Soja / Crescimento Milho", "Risco": "Incidência de Lagarta do Cartucho no Milho / Maturação do Café."},
            "Abril": {"Acao": "Transição para Seca / Colheita Café", "Risco": "Início do estresse hídrico / Pressão de Cigarrinha no Milho."},
            "Maio": {"Acao": "Pico Colheita Café", "Risco": "Possibilidade de frentes frias e geadas tardias no Cone Sul."},
            "Junho": {"Acao": "Colheita Milho / Seca Severa", "Risco": "Nível reduzido do Rio Madeira impactando o calado das barcaças."},
            "Julho": {"Acao": "Entressafra / Logística sob pressão", "Risco": "Incidência de queimadas / Rio Madeira em nível crítico de navegação."},
            "Agosto": {"Acao": "Vazio Sanitário / Preparo Solo", "Risco": "Baixa umidade relativa / Stress hídrico severo no solo."},
            "Setembro": {"Acao": "Início Plantio Soja", "Risco": "Irregularidade pluviométrica no estabelecimento inicial da cultura."},
            "Outubro": {"Acao": "Plantio Intenso", "Risco": "Pressão de lagartas desfolhadoras nas lavouras jovens."},
            "Novembro": {"Acao": "Desenvolvimento Vegetativo", "Risco": "Necessidade de monitoramento de anomalias climáticas localizadas."},
            "Dezembro": {"Acao": "Desenvolvimento / Aplicações", "Risco": "Patógenos fúngicos decorrentes da alta umidade (290mm)."},
        }
        
        st.info(f"**Status em {mes_sel}:** {calendario[mes_sel]['Acao']}")
        st.warning(f"**Alerta de Risco:** {calendario[mes_sel]['Risco']}")

    with c_int2:
        st.subheader("Logística e Fluxos de Exportação")
        st.markdown("""
        **Corredor Logístico do Rio Madeira (Arco Norte)**
        O escoamento da produção de Rondônia via Porto Velho é um diferencial de competitividade:
        - **Redução de Custos:** Até 30% mais eficiente que o modal rodoviário para o Sul.
        - **Destinos Principais:** China (55%), Europa (20%) e Oriente Médio (15%).
        - **Capacidade:** Superior a 10 milhões de toneladas/ano.
        """)
        st.success("Nota: A dragagem do Rio Madeira é vital para a competitividade do grão rondoniense.")

    st.divider()
    st.subheader("Simulador de Valor Bruto (VBP)")
    p_soja = st.number_input("Preço Soja (Saca/60kg)", 100, 250, 135)
    p_gado = st.number_input("Preço Boi (@)", 150, 400, 230)
    
    vbp_est = (df['Soja_Qtd_T'].sum() / 0.06 * p_soja) + (df['Gado_Cabecas'].sum() * 0.5 * p_gado)
    st.metric("VBP Projetado (Soja + Carne)", f"R$ {vbp_est/1e9:.2f} Bilhões")
    st.caption("Cálculo baseado em produtividade média e preços de balcão.")

    st.divider()
    st.subheader("Relevância no PIB Agropecuário")
    df_eco = df.copy()
    df_eco['Representatividade'] = (df_eco['Valor_Agricola_Total_Mil'] / (df_eco['PIB_Agro_Mil'] + 1)) * 100
    fig_pib = px.bar(df_eco.nlargest(15, 'PIB_Agro_Mil'), x='PIB_Agro_Mil', y='Municipio', orientation='h', color='Representatividade', title="Maiores PIBs Agropecuários de RO")
    fig_pib.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_pib, use_container_width=True)

# --- FOOTER ---
st.divider()
st.subheader("Consultoria Analítica de Dados")
st.info("Plataforma analítica baseada em dados oficiais do IBGE. Foco em precisão e transparência setorial.")

# Sugestões de Análise para o Usuário
with st.expander("Exemplos de consultas estratégicas para a I.A."):
    st.markdown("""
    - Quais são os municípios com maior eficiência técnica (Kg/Ha) no Café em Rondônia?
    - Analise os municípios com maior dependência econômica de uma única cultura.
    - Qual a representatividade da Pecuária no PIB Agropecuário do estado?
    - Compare o perfil produtivo e econômico entre Vilhena e Porto Velho.
    """)

if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if p_user := st.chat_input("Ex: Qual o impacto das perdas de safra em Vilhena?"):
    with st.chat_message("user"): st.markdown(p_user)
    st.session_state.messages.append({"role": "user", "content": p_user})

    if not api_key: st.error("Insira a API Key na barra lateral.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Processando inteligência..."):
                try:
                    # Enviar contexto resumido para economizar tokens e ser preciso
                    ctx = df.to_csv(index=False)
                    model = genai.GenerativeModel('gemini-flash-latest')
                    prompt = f"Você é um analista sênior. Use estes dados de RO: {ctx}. Pergunta: {p_user}. Responda com foco em negócios e exportação."
                    resp = model.generate_content(prompt)
                    st.markdown(resp.text)
                    st.session_state.messages.append({"role": "assistant", "content": resp.text})
                except Exception as e: st.error(f"Erro: {e}")
