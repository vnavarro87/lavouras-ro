import requests
import pandas as pd
import os
import time

def buscar_variavel(tabela, variavel, classif, item):
    url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/n6/in%20n3%2011/v/{variavel}/p/last"
    if classif:
        url += f"/{classif}/{item}"
    
    try:
        res = requests.get(url, timeout=20)
        if res.status_code == 200: return res.json()
    except: return None
    return None

def coleta_agro_ro_final_v18():
    pasta = os.path.dirname(__file__)
    
    # Configuração das Tabelas e Produtos
    # Tabela 1612: Cereais, Leguminosas e Oleaginosas (Temporárias)
    # Tabela 1613: Lavoura Permanente
    config_agri = [
        {"tabela": 1612, "classif": "c81", "produtos": {"Soja": 2713, "Milho": 2711}},
        {"tabela": 1613, "classif": "c82", "produtos": {"Cafe": 2723, "Cacau": 2722}}
    ]
    
    # 214=Qtd, 215=Valor, 112=Produtividade, 109=Área Plantada, 110=Área Colhida
    metricas = {"214": "Qtd_T", "215": "Valor_Mil", "112": "Prod_KgHa", "109": "AreaPlant_Ha", "110": "AreaColh_Ha"}
    df_mestre = pd.DataFrame()

    for config in config_agri:
        for nome_prod, cod_prod in config["produtos"].items():
            print(f"--- Coletando {nome_prod} (Tabela {config['tabela']}) ---")
            df_prod = pd.DataFrame()
            for cod_var, sufixo in metricas.items():
                dados = buscar_variavel(config["tabela"], cod_var, config["classif"], cod_prod)
                if dados and len(dados) > 1:
                    df_temp = pd.DataFrame(dados[1:])
                    df_temp = df_temp[['D1N', 'V']].copy()
                    df_temp.columns = ['Municipio', f"{nome_prod}_{sufixo}"]
                    df_temp['Municipio'] = df_temp['Municipio'].str.replace(' - RO', '', regex=False)
                    df_temp[f"{nome_prod}_{sufixo}"] = pd.to_numeric(df_temp[f"{nome_prod}_{sufixo}"], errors='coerce').fillna(0)
                    
                    if df_prod.empty: 
                        df_prod = df_temp
                    else: 
                        df_prod = pd.merge(df_prod, df_temp, on="Municipio", how="outer")
                time.sleep(0.5) # Pausa para evitar bloqueio da API
            
            if df_mestre.empty: 
                df_mestre = df_prod
            else: 
                df_mestre = pd.merge(df_mestre, df_prod, on="Municipio", how="outer")

    # VALOR TOTAL DA PRODUÇÃO E PIB
    print("--- Coletando Dados Econômicos (PIB e Valor Total) ---")
    # Valor Total
    vt = buscar_variavel(1612, "215", "c81", "0") # Total Lavoura Temporária
    vp = buscar_variavel(1613, "215", "c82", "0") # Total Lavoura Permanente
    
    if vt and len(vt) > 1:
        df_vt = pd.DataFrame(vt[1:]); df_vt = df_vt[['D1N', 'V']]; df_vt.columns=['Municipio', 'V1612']
        df_vt['Municipio'] = df_vt['Municipio'].str.replace(' - RO', '')
        df_vt['V1612'] = pd.to_numeric(df_vt['V1612'], errors='coerce').fillna(0)
        df_mestre = pd.merge(df_mestre, df_vt, on="Municipio", how="outer")

    if vp and len(vp) > 1:
        df_vp = pd.DataFrame(vp[1:]); df_vp = df_vp[['D1N', 'V']]; df_vp.columns=['Municipio', 'V1613']
        df_vp['Municipio'] = df_vp['Municipio'].str.replace(' - RO', '')
        df_vp['V1613'] = pd.to_numeric(df_vp['V1613'], errors='coerce').fillna(0)
        df_mestre = pd.merge(df_mestre, df_vp, on="Municipio", how="outer")

    df_mestre['Valor_Agricola_Total_Mil'] = df_mestre.get('V1612', 0) + df_mestre.get('V1613', 0)

    # PIB Agro
    pib = buscar_variavel(5938, "37", None, None)
    if pib and len(pib) > 1:
        df_pib = pd.DataFrame(pib[1:]); df_pib = df_pib[['D1N', 'V']]; df_pib.columns=['Municipio', 'PIB_Agro_Mil']
        df_pib['Municipio'] = df_pib['Municipio'].str.replace(' - RO', '')
        df_pib['PIB_Agro_Mil'] = pd.to_numeric(df_pib['PIB_Agro_Mil'], errors='coerce').fillna(0)
        df_mestre = pd.merge(df_mestre, df_pib, on="Municipio", how="outer")

    # PECUÁRIA
    print("--- Coletando Pecuária ---")
    g = buscar_variavel(3939, "105", "c79", "2670")
    if g and len(g) > 1:
        df_g = pd.DataFrame(g[1:]); df_g = df_g[['D1N', 'V']]; df_g.columns=['Municipio', 'Gado_Cabecas']
        df_g['Municipio'] = df_g['Municipio'].str.replace(' - RO', '')
        df_g['Gado_Cabecas'] = pd.to_numeric(df_g['Gado_Cabecas'], errors='coerce').fillna(0)
        df_mestre = pd.merge(df_mestre, df_g, on="Municipio", how="outer")

    l = buscar_variavel(74, "106", "c80", "2682")
    if l and len(l) > 1:
        df_l = pd.DataFrame(l[1:]); df_l = df_l[['D1N', 'V']]; df_l.columns=['Municipio', 'Leite_Mil_Litros']
        df_l['Municipio'] = df_l['Municipio'].str.replace(' - RO', '')
        df_l['Leite_Mil_Litros'] = pd.to_numeric(df_l['Leite_Mil_Litros'], errors='coerce').fillna(0)
        df_mestre = pd.merge(df_mestre, df_l, on="Municipio", how="outer")

    df_mestre = df_mestre.fillna(0)
    df_mestre.to_csv(os.path.join(pasta, "dados_agro_ro_master.csv"), index=False)
    print("Dados V18 Auditados e Gerados com Sucesso.")

if __name__ == "__main__":
    coleta_agro_ro_final_v18()
