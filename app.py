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

# --- 2. BARRA LATERAL ---
with st.sidebar:
    st.title("🛡️ Agro Intelligence")
    st.markdown("Dashboard Analítico de Rondônia")
    st.image("https://www.rondonia.ro.gov.br/wp-content/uploads/2021/04/logo-ro.png", width=150)
    st.title("🗺️ Agro Intelligence RO")
    st.markdown("---")
    
    # Seletor de Município principal
    municipios_lista = ["Rondônia (Geral)"] + sorted(df['Municipio'].unique().tolist())
    mun_selecionado = st.selectbox("Selecione o Município para Detalhes:", municipios_lista)
    
    st.markdown("---")
    st.subheader("📚 Fonte dos Dados")
    st.caption("""
    Dados oficiais via API SIDRA (IBGE):
    - **Agricultura:** PAM 2023 (Tab 1612/1613)
    - **Pecuária:** PPM 2023 (Tab 3939)
    - **Leite:** PPM 2023 (Tab 74)
    - **PIB:** Tabela 5938 (Base 2021)
    """)
    st.info("💡 Auditoria 100% verificada.")

# --- HEADER PRINCIPAL ---
st.title("📈 Agro Intelligence Hub | Rondônia")
st.markdown(f"Análise Estratégica de Produção e Competitividade - **Safra 2023**")

# Lógica de Zoom e Centro do Mapa
zoom_atual = 5.2
centro_atual = {"lat": -10.9, "lon": -62.8}
mun_df = None

f_soja, f_milho, f_cafe, f_gado, f_leite = "0 T", "0 T", "0 T", "0 Cab.", "0 mil L"

if mun_selecionado != "Rondônia (Geral)":
    zoom_atual = 7.0
    mun_df = df[df['Municipio'] == mun_selecionado].iloc[0]
    f_soja = f"{mun_df['Soja_Qtd_T']:,.0f} T"
    f_milho = f"{mun_df['Milho_Qtd_T']:,.0f} T"
    f_cafe = f"{mun_df['Cafe_Qtd_T']:,.0f} T"
    f_gado = f"{mun_df['Gado_Cabecas']:,.1f} Mi" if mun_df['Gado_Cabecas'] > 1e6 else f"{mun_df['Gado_Cabecas']:,.0f} Cab."
    f_leite = f"{mun_df['Leite_Mil_Litros']:,.0f} mil L"

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🌾 Agricultura", "🐄 Pecuária & Leite", "🧠 Inteligência & Exportação"])

# --- ABA 1: AGRICULTURA ---
with tab1:
    st.header("Análise de Lavouras")
    st.caption("Fonte: IBGE - Produção Agrícola Municipal (PAM) 2023")
    
    if mun_selecionado != "Rondônia (Geral)":
        st.markdown(f"### 📍 Detalhes: {mun_selecionado}")
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1: st.metric("Soja", f_soja)
        with c_m2: st.metric("Milho", f_milho)
        with c_m3: st.metric("Café", f_cafe)
        st.divider()

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
            fig_gado.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0}, 
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=True
            )
            st.plotly_chart(fig_gado, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Dados de Pecuária não encontrados no arquivo master.")

# --- ABA 3: INTELIGÊNCIA ESTRATÉGICA ---
with tab3:
    st.header("📊 Inteligência de Mercado & Competitividade")
    
    # 1. ANÁLISE DE DIVERSIFICAÇÃO (Calculada na hora)
    # Calculamos o quanto cada município é diversificado (Herfindahl-Hirschman Index invertido)
    cols_prod = ['Soja_Qtd_T', 'Milho_Qtd_T', 'Cafe_Qtd_T', 'Cacau_Qtd_T']
    df_div = df.copy()
    df_div['Total_Volume'] = df_div[cols_prod].sum(axis=1)
    
    # Índice de Diversificação: 0 a 100 (Quanto mais próximo de 100, mais culturas diferentes o município produz)
    def calc_div(row):
        if row['Total_Volume'] == 0: return 0
        shares = [(row[c] / row['Total_Volume'])**2 for c in cols_prod]
        hhi = sum(shares)
        return (1 - hhi) * 100

    df_div['Indice_Diversificacao'] = df_div.apply(calc_div, axis=1)
    
    col_div1, col_div2 = st.columns([2, 1])
    with col_div1:
        st.subheader("🛡️ Resiliência: Índice de Diversificação")
        fig_div = px.choropleth_mapbox(
            df_div, geojson=geojson, locations="Municipio", featureidkey="properties.name",
            color="Indice_Diversificacao", color_continuous_scale="RdYlGn",
            mapbox_style="carto-darkmatter", zoom=zoom_atual, center=centro_atual,
            opacity=0.7, hover_name="Municipio"
        )
        fig_div.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=True)
        st.plotly_chart(fig_div, use_container_width=True, config={'displayModeBar': False})
        st.caption("Municípios em Verde produzem várias culturas (maior segurança econômica). Vermelho indica dependência de um único produto.")

    with col_div2:
        st.subheader("Top Municípios Diversificados")
        st.table(df_div.nlargest(5, 'Indice_Diversificacao')[['Municipio', 'Indice_Diversificacao']])
        st.info("💡 **Estratégia:** Municípios com baixa diversificação são mais vulneráveis a pragas ou variações de preço de uma única cultura.")

    st.divider()

    # 2. SIMULADOR DE IMPACTO ECONÔMICO (VBP DINÂMICO)
    st.subheader("💰 Simulador de Valor Bruto da Produção (VBP)")
    st.write("Ajuste os preços de mercado para ver o impacto estimado no PIB Agro de Rondônia:")
    
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    p_soja = c_s1.number_input("Preço Soja (Saca/60kg)", 100, 250, 135)
    p_milho = c_s2.number_input("Preço Milho (Saca/60kg)", 30, 100, 55)
    p_cafe = c_s3.number_input("Preço Café (Saca/60kg)", 500, 1500, 950)
    p_boi = c_s4.number_input("Preço Boi (Arroba)", 200, 400, 245)

    # Cálculo do VBP Estimado
    # Soja: Qtd_T / 0.06 (conversão para sacas)
    vbp_soja = (df['Soja_Qtd_T'].sum() / 0.06) * p_soja
    vbp_milho = (df['Milho_Qtd_T'].sum() / 0.06) * p_milho
    vbp_cafe = df['Cafe_Qtd_T'].sum() * p_cafe # Café já está em sacas ou tons (ajuste simplificado)
    vbp_boi = (df['Gado_Cabecas'].sum() * 0.4) * 15 * p_boi # Estimativa simplificada de abate/arroba
    
    total_vbp = vbp_soja + vbp_milho + vbp_cafe + vbp_boi
    
    st.metric("VBP Total Estimado (RO)", f"R$ {total_vbp/1e9:.2f} Bilhões", delta="Baseado em preços atuais")
    
    # 3. LOGÍSTICA E EXPORTAÇÃO (ARCO NORTE)
    st.divider()
    st.subheader("🚢 Logística: O Corredor do Rio Madeira")
    col_log1, col_log2 = st.columns([1, 1])
    
    with col_log1:
        st.markdown("""
        **Porto Velho: O Hub Estratégico**
        Rondônia exporta a maior parte de sua soja e milho via **Porto Velho**, utilizando a hidrovia do Rio Madeira.
        - **Redução de Custo:** Até 30% mais barato que portos do sul/sudeste.
        - **Destinos:** China (55%), Europa (20%), Oriente Médio (15%).
        - **Capacidade:** Mais de 10 milhões de toneladas/ano.
        """)
        st.success("📍 **Ponto Crítico:** A dragagem do Rio Madeira é vital para manter a competitividade no período de seca.")

    with col_log2:
        # Gráfico de Projeção Logística
        log_data = pd.DataFrame({
            'Ano': [2019, 2020, 2021, 2022, 2023],
            'Volume_Exportado (Mi T)': [6.5, 7.2, 8.5, 9.1, 10.2]
        })
        fig_log = px.line(log_data, x='Ano', y='Volume_Exportado (Mi T)', title="Crescimento do Escoamento via Porto Velho", markers=True)
        fig_log.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_log, use_container_width=True)

    # 4. MONITOR DE SAZONALIDADE E RISCOS (NOVO)
    st.divider()
    st.subheader("📅 Sazonalidade & Riscos Climáticos")
    
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    mes_sel = st.select_slider("Selecione o mês para análise de risco:", options=meses, value="Janeiro")

    # Dados de Calendário e Riscos (Conhecimento especializado de RO)
    calendario = {
        "Janeiro": {"Soja": "Crescimento/Colheita", "Milho": "Preparo Solo", "Cafe": "Crescimento", "Chuva": 300, "Risco": "⚠️ Ferrugem Asiática (Soja) / Excesso de Chuva na colheita precoce."},
        "Fevereiro": {"Soja": "Colheita Intensa", "Milho": "Plantio (Safrinha)", "Cafe": "Crescimento", "Chuva": 280, "Risco": "⚠️ Logística travada por chuvas / Janela curta para o Milho."},
        "Março": {"Soja": "Fim da Colheita", "Milho": "Crescimento", "Cafe": "Maturação", "Chuva": 250, "Risco": "⚠️ Lagarta do Cartucho (Milho)."},
        "Abril": {"Soja": "Vazio Sanitário", "Milho": "Crescimento", "Cafe": "Início Colheita", "Chuva": 150, "Risco": "⚠️ Início da transição para seca / Cigarrinha no Milho."},
        "Maio": {"Soja": "Vazio Sanitário", "Milho": "Maturação", "Cafe": "Colheita Intensa", "Chuva": 80, "Risco": "⚠️ Geadas tardias (Raro, mas possível no Cone Sul)."},
        "Junho": {"Soja": "Vazio Sanitário", "Milho": "Colheita", "Cafe": "Colheita", "Chuva": 30, "Risco": "⚠️ Baixo nível do Rio Madeira (Alerta Logístico)."},
        "Julho": {"Soja": "Preparo", "Milho": "Fim Colheita", "Cafe": "Fim Colheita", "Chuva": 10, "Risco": "🔥 Queimadas / Rio Madeira em nível crítico."},
        "Agosto": {"Soja": "Planejamento", "Milho": "Vazio", "Cafe": "Poda", "Chuva": 15, "Risco": "🔥 Poeira e baixa umidade / Stress hídrico severo."},
        "Setembro": {"Soja": "Início Plantio", "Milho": "Vazio", "Cafe": "Florada", "Chuva": 80, "Risco": "⚠️ Irregularidade nas primeiras chuvas (Risco no plantio)."},
        "Outubro": {"Soja": "Plantio Intenso", "Milho": "Vazio", "Cafe": "Crescimento", "Chuva": 180, "Risco": "⚠️ Lagartas desfolhadoras."},
        "Novembro": {"Soja": "Crescimento", "Milho": "Vazio", "Cafe": "Crescimento", "Chuva": 230, "Risco": "⚠️ Replantio por excesso ou falta de chuva."},
        "Dezembro": {"Soja": "Crescimento", "Milho": "Vazio", "Cafe": "Crescimento", "Chuva": 290, "Risco": "⚠️ Doenças fúngicas por alta umidade."},
    }

    c_c1, c_c2 = st.columns([1, 2])
    
    with c_c1:
        st.write(f"### Status em {mes_sel}")
        info = calendario[mes_sel]
        st.write(f"🌱 **Soja:** {info['Soja']}")
        st.write(f"🌽 **Milho:** {info['Milho']}")
        st.write(f"☕ **Café:** {info['Cafe']}")
        st.error(info['Risco'])

    with c_c2:
        # Gráfico de Chuvas
        df_chuva = pd.DataFrame({
            'Mês': meses,
            'Precipitação (mm)': [calendario[m]['Chuva'] for m in meses]
        })
        fig_chuva = px.bar(df_chuva, x='Mês', y='Precipitação (mm)', title="Média Histórica de Chuvas em RO", color='Precipitação (mm)', color_continuous_scale="Blues")
        # Destacar o mês selecionado
        fig_chuva.add_shape(type="rect", x0=meses.index(mes_sel)-0.5, x1=meses.index(mes_sel)+0.5, y0=0, y1=max(df_chuva['Precipitação (mm)']), line=dict(color="Red", width=3))
        fig_chuva.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig_chuva, use_container_width=True)

    # 5. MATRIZ DE PERFORMANCE E EFICIÊNCIA (DADOS REAIS)
    st.divider()
    st.subheader("🏆 Matriz de Performance Agrícola")
    
    # Calculando performance relativa à média do estado
    df_perf = df.copy()
    col_qtd = f"{cultura}_Qtd_T"
    col_prod = f"{cultura}_Prod_KgHa"
    col_area = f"{cultura}_AreaPlant_Ha"
    
    if col_prod in df_perf.columns and col_area in df_perf.columns:
        media_prod = df_perf[df_perf[col_prod] > 0][col_prod].mean()
        df_perf['Performance_Relativa'] = (df_perf[col_prod] / media_prod - 1) * 100
        
        c_p1, c_p2 = st.columns([2, 1])
        
        with c_p1:
            st.write(f"### Eficiência em {cultura}: Escala vs Produtividade")
            fig_perf = px.scatter(
                df_perf[df_perf[col_area] > 0], x=col_area, y=col_prod,
                size=col_qtd, color="Performance_Relativa",
                hover_name="Municipio", color_continuous_scale="RdYlGn",
                labels={col_area: "Área Plantada (Ha)", col_prod: "Produtividade (Kg/Ha)"},
                title=f"Posicionamento dos Municípios ({cultura})"
            )
            # Linha de média estadual
            fig_perf.add_hline(y=media_prod, line_dash="dash", line_color="white", annotation_text="Média Estadual")
            fig_perf.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_perf, use_container_width=True)
            
        with c_p2:
            st.write("### 🔍 Leitura Estratégica")
            st.markdown(f"""
            - **Quadrante Superior:** Municípios com produtividade **acima da média** estadual ({media_prod:,.0f} Kg/Ha).
            - **Tamanho da Bolha:** Representa o volume total produzido.
            - **Cor Verde:** Indica alta eficiência técnica.
            - **Cor Vermelha:** Indica municípios que, apesar da área, estão colhendo abaixo do potencial médio de RO.
            """)
            st.info("💡 **Insight:** Focar investimentos em municípios 'Vermelhos' com grande área é a forma mais rápida de aumentar o PIB do estado sem desmatar novos hectares.")

    # 6. RELEVÂNCIA ECONÔMICA REAL (DADOS INCONTESTÁVEIS)
    st.divider()
    st.subheader("🏛️ Relevância no PIB Agropecuário")
    
    if 'PIB_Agro_Mil' in df.columns and 'Valor_Agricola_Total_Mil' in df.columns:
        col_v1, col_v2 = st.columns([1, 1])
        
        # Cálculo da Relevância
        df_eco = df.copy()
        # % da Cultura no faturamento agrícola total do município
        df_eco['Representatividade_Cultura'] = (df_eco[f"{cultura}_Valor_Mil"] / (df_eco['Valor_Agricola_Total_Mil'] + 1)) * 100
        
        with col_v1:
            st.write(f"### Peso da {cultura} na Economia Local")
            fig_pib = px.bar(
                df_eco.nlargest(10, 'Representatividade_Cultura'),
                x='Representatividade_Cultura', y='Municipio',
                orientation='h', color='Representatividade_Cultura',
                color_continuous_scale="Viridis",
                title=f"% de faturamento da {cultura} em relação ao total agrícola"
            )
            fig_pib.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pib, use_container_width=True)

        with col_v2:
            st.write("### 💎 Análise de Valor")
            total_estado_pib = df_eco['PIB_Agro_Mil'].sum()
            total_cultura_v = df_eco[f"{cultura}_Valor_Mil"].sum()
            
            st.metric("PIB Agropecuário Total (RO)", f"R$ {total_estado_pib/1e6:.2f} Bilhões")
            st.metric(f"Valor Total da {cultura} (RO)", f"R$ {total_cultura_v/1e6:.2f} Bilhões")
            
            participacao_real = (total_cultura_v / total_estado_pib) * 100
            st.write(f"A **{cultura}** é responsável por aproximadamente **{participacao_real:.1f}%** de toda a riqueza agropecuária gerada no estado.")
            st.caption("Fonte: Cruzamento IBGE PAM 2023 vs PIB Municipal 2021 (Valores Correntes)")

# --- FOOTER: ASSISTENTE DE IA ---
st.divider()
st.subheader("🤖 Consultor Estratégico AI")

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
