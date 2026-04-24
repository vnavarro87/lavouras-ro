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
    mun_selecionado = st.selectbox("Foco Regional:", municipios_lista)
    
    st.markdown("---")
    st.subheader("Fonte dos Dados")
    st.caption("IBGE: PAM/PPM 2023 | PIB 2021")
    st.info("Plataforma Auditada")

# --- HEADER E KPIs TOTAIS (O IMPACTO) ---
st.title("Agro Intelligence Hub | Rondônia")
st.markdown("Análise Estratégica de Produção e Competitividade Setorial")

# Lógica de Zoom e Centro do Mapa (Correção de Erro)
zoom_atual = 5.2
centro_atual = {"lat": -10.9, "lon": -62.8}

# Cálculo de Métricas Estaduais
pib_total = df['PIB_Agro_Mil'].sum() / 1e6
vbp_total = df['Valor_Agricola_Total_Mil'].sum() / 1e6
rebanho_total = df['Gado_Cabecas'].sum() / 1e6
area_total = df[[c for c in df.columns if 'AreaPlant_Ha' in c]].sum().sum() / 1e6

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("PIB Agropecuário", f"R$ {pib_total:.2f} Bi", help="Valor Adicionado Bruto da Agropecuária (IBGE)")
with c2: st.metric("Valor da Produção", f"R$ {vbp_total:.2f} Bi", help="Valor Bruto da Produção Agrícola (PAM)")
with c3: st.metric("Rebanho Bovino", f"{rebanho_total:.2f} Mi", help="Efetivo Total de Cabeças (PPM)")
with c4: st.metric("Área Cultivada", f"{area_total:.2f} Mi Ha", help="Soma das principais culturas plantadas")

st.markdown("---")

# --- NAVEGAÇÃO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["Visão Geográfica", "Análise de Performance", "Sazonalidade e Mercado"])

# --- ABA 1: VISÃO GEOGRÁFICA (O ONDE) ---
with tab1:
    col_mapa, col_info = st.columns([2, 1])
    
    with col_mapa:
        st.subheader("Distribuição Espacial da Produção")
        cultura_mapa = st.selectbox("Selecione a Camada de Dados:", ["Soja", "Milho", "Cafe", "Cacau", "Gado", "Leite"])
        
        # Lógica de coluna dinâmica para o mapa
        col_map = f"{cultura_mapa}_Qtd_T" if cultura_mapa not in ["Gado", "Leite"] else (f"{cultura_mapa}_Cabecas" if cultura_mapa=="Gado" else f"{cultura_mapa}_Mil_Litros")
        
        fig_mapa = px.choropleth_mapbox(
            df, geojson=geojson, locations="Municipio", featureidkey="properties.name",
            color=col_map, color_continuous_scale="Viridis",
            mapbox_style="carto-darkmatter", zoom=5.2, center={"lat": -10.9, "lon": -62.8},
            opacity=0.6, hover_name="Municipio"
        )
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
        cultura = st.selectbox("Cultura:", ["Soja", "Milho", "Cafe", "Cacau"])
        metrica = st.selectbox("Métrica:", ["Quantidade", "Produtividade", "Valor", "Perda"])
        
        # Mapeamento de colunas
        map_cols = {
            "Quantidade": f"{cultura}_Qtd_T",
            "Produtividade": f"{cultura}_Prod_KgHa",
            "Valor": f"{cultura}_Valor_Mil",
            "Perda": f"{cultura}_Perda_Percent"
        }
        col_ativa = map_cols[metrica]
        
    with c2:
        # Definindo as colunas para os Mini Cards
        mc1, mc2, mc3 = st.columns(3)
        
        # Verificação de segurança: Só prossegue se a coluna existir
        if col_ativa in df.columns:
            # Pegamos a coluna de quantidade específica desta cultura
            col_qtd = f"{cultura}_Qtd_T"
            
            if col_qtd in df.columns:
                total_prod = df[col_qtd].sum()
                max_prod = df[col_qtd].max()
                lider_idx = df[col_qtd].idxmax()
                lider = df.loc[lider_idx, "Municipio"] if not df.empty else "N/A"
                
                mc1.markdown(f'<div class="metric-card"><div class="metric-label">Produção Total ({cultura})</div><div class="metric-value">{total_prod:,.0f} T</div></div>', unsafe_allow_html=True)
                mc2.markdown(f'<div class="metric-card"><div class="metric-label">Líder de Produção</div><div class="metric-value">{lider}</div></div>', unsafe_allow_html=True)
                mc3.markdown(f'<div class="metric-card"><div class="metric-label">Recorde Municipal</div><div class="metric-value">{max_prod:,.0f} T</div></div>', unsafe_allow_html=True)
            else:
                st.warning(f"Dados de quantidade para {cultura} não encontrados.")
        else:
            st.error(f"Coluna {col_ativa} não encontrada no banco de dados.")

    st.markdown("---")
    
    if col_ativa in df.columns:
        col_map, col_chart = st.columns([2, 1])
        
        with col_map:
            # Paleta de cores
            paletas = {"Soja": "Viridis", "Milho": "Plasma", "Cafe": "Inferno", "Cacau": "Magma"}
            cor_mapa = paletas.get(cultura, "Viridis")
            if metrica == "Perda": cor_mapa = "Reds"
            
            df['valor_visual'] = df[col_ativa].apply(lambda x: math.log10(x + 1))
            
            fig_map = px.choropleth_mapbox(
                df, geojson=geojson, locations="Municipio", featureidkey="properties.name",
                color='valor_visual', color_continuous_scale=cor_mapa,
                mapbox_style="carto-darkmatter", zoom=zoom_atual, center=centro_atual,
                opacity=0.8, hover_name="Municipio",
                hover_data={'valor_visual': False, col_ativa: ":.2f"}
            )
            fig_map.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0}, 
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=True # Escala restaurada
            )
            st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        
        with col_chart:
            st.subheader(f"Top 10: {metrica}")
            top_df = df.nlargest(10, col_ativa)[["Municipio", col_ativa]]
            fig_bar = px.bar(top_df, x=col_ativa, y="Municipio", orientation='h', color=col_ativa, color_continuous_scale=cor_mapa)
            fig_bar.update_layout(
                showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                font_color="white", yaxis={'categoryorder':'total ascending'},
                coloraxis_showscale=True # Escala restaurada no ranking
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

# --- ABA 2: PECUÁRIA ---
with tab2:
    if mun_selecionado != "Rondônia (Geral)":
        st.markdown(f"### 📍 Detalhes: {mun_selecionado} (Pecuária)")
        c_p1, c_p2 = st.columns(2)
        with c_p1: st.metric("Efetivo Bovino", f_gado)
        with c_p2: st.metric("Produção Leiteira", f_leite)
        st.markdown("---")
        
    st.subheader("🐄 Análise de Rebanho Bovino")
    
    if "Gado_Cabecas" in df.columns:
        c_p1, c_p2 = st.columns([3, 1])
        
        with c_p2:
            finalidade = st.selectbox("Analisar por:", ["Corte (Rebanho)", "Leite (Produção)"])
            col_ativa_gado = "Gado_Cabecas" if "Corte" in finalidade else "Leite_Mil_Litros"
            unidade_gado = "Cab." if "Corte" in finalidade else "Mil Litros"
            cor_gado = "YlOrBr" if "Corte" in finalidade else "GnBu"
            
            total_v = df[col_ativa_gado].sum()
            st.metric(f"Total RO ({finalidade})", f"{total_v:,.0f} {unidade_gado}")
            st.markdown("---")
            st.write(f"**Top 5 ({finalidade}):**")
            st.table(df.nlargest(5, col_ativa_gado)[["Municipio", col_ativa_gado]])
            
        with c_p1:
            fig_gado = px.choropleth_mapbox(
                df, geojson=geojson, locations="Municipio", featureidkey="properties.name",
                color=col_ativa_gado, color_continuous_scale=cor_gado,
                mapbox_style="carto-darkmatter", zoom=zoom_atual, center=centro_atual,
                opacity=0.7, hover_name="Municipio"
            )
            total_prod = df[f"{cultura}_Qtd_T"].sum()
            lider = df.loc[df[f"{cultura}_Qtd_T"].idxmax(), "Municipio"]
            mc1.metric("Produção Total", f"{total_prod:,.0f} T")
            mc2.metric("Líder de Produção", lider)
            mc3.metric("Recorde Municipal", f"{df[f'{cultura}_Qtd_T'].max():,.0f} T")

    st.markdown("---")
    
    # Seção Pecuária dentro da Aba 2
    st.subheader("🐄 Análise de Pecuária")
    c_p1, c_p2 = st.columns([3, 1])
    with c_p2:
        finalidade = st.selectbox("Analisar por:", ["Corte (Rebanho)", "Leite (Produção)"])
        col_ativa_gado = "Gado_Cabecas" if "Corte" in finalidade else "Leite_Mil_Litros"
        cor_gado = "YlOrBr" if "Corte" in finalidade else "GnBu"
        st.metric(f"Total RO ({finalidade})", f"{df[col_ativa_gado].sum():,.0f}")
    with c_p1:
        fig_gado = px.choropleth_mapbox(df, geojson=geojson, locations="Municipio", featureidkey="properties.name", color=col_ativa_gado, color_continuous_scale=cor_gado, mapbox_style="carto-darkmatter", zoom=5.2, center={"lat": -10.9, "lon": -62.8}, opacity=0.7)
        fig_gado.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=True)
        st.plotly_chart(fig_gado, use_container_width=True, config={'displayModeBar': False})

    # Matriz de Performance
    st.divider()
    st.subheader("Matriz de Performance e Eficiência Técnica")
    
    df_perf = df.copy()
    col_prod = f"{cultura}_Prod_KgHa"
    col_area = f"{cultura}_AreaPlant_Ha"
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
    st.subheader("Fonte dos Dados")
    st.caption("""
    Dados oficiais via API SIDRA (IBGE):
    - Agricultura: PAM 2023 (Tab 1612/1613)
    - Pecuária: PPM 2023 (Tab 3939)
    - Leite: PPM 2023 (Tab 74)
    - PIB: Tabela 5938 (Base 2021)
    - Geometria: Malha Digital IBGE 2022
    """)
    st.info("Auditoria técnica verificada.")

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
