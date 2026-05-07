"""
Coleta de dados de produção de soja em Rondônia via API SIDRA (IBGE).

Tabela 1612 - Produção Agrícola Municipal (PAM)
Produto: Soja (código 2713)
Variáveis: Quantidade (214), Valor (215), Produtividade (112), Área Plantada (109)
"""
import requests
import pandas as pd
import os
import time

CODIGO_SOJA = 2713
TABELA_PAM = 1612
CLASSIFICACAO = "c81"

METRICAS = {
    "214": "Soja_Qtd_T",
    "215": "Soja_Valor_Mil",
    "112": "Soja_Prod_KgHa",
    "109": "Soja_AreaPlant_Ha",
}

# Códigos especiais do SIDRA (https://sidra.ibge.gov.br)
# "-"   = fenômeno não existe
# ".."  = não se aplica
# "..." = dado não disponível
# "X"   = dado omitido por sigilo estatístico (município com poucos produtores)
# Todos são consolidados como 0 no CSV master; a distinção entre sigilo e zero
# verdadeiro é tratada como limitação documentada em README.md / METODOLOGIA.md.
CODIGOS_ESPECIAIS = {"-", "..", "...", "X"}


def buscar_variavel(tabela, variavel, classificacao, item):
    url = (
        f"https://apisidra.ibge.gov.br/values/t/{tabela}"
        f"/n6/in%20n3%2011/v/{variavel}/p/last/{classificacao}/{item}"
    )
    try:
        res = requests.get(url, timeout=20)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException as e:
        print(f"Falha na requisição (var {variavel}): {e}")
    return None


def coletar_soja_ro():
    pasta = os.path.dirname(__file__)
    df_mestre = pd.DataFrame()
    relatorio = {}

    for cod_var, nome_col in METRICAS.items():
        print(f"Coletando {nome_col} (variável {cod_var})...")
        dados = buscar_variavel(TABELA_PAM, cod_var, CLASSIFICACAO, CODIGO_SOJA)
        if not dados or len(dados) <= 1:
            print(f"  Sem dados retornados para {nome_col}")
            continue

        df_temp = pd.DataFrame(dados[1:])[["D1N", "V"]].copy()
        df_temp.columns = ["Municipio", nome_col]
        df_temp["Municipio"] = df_temp["Municipio"].str.replace(" - RO", "", regex=False)

        # Auditoria de códigos especiais antes de converter
        contagem_especiais = (
            df_temp[nome_col].astype(str).isin(CODIGOS_ESPECIAIS).sum()
        )
        relatorio[nome_col] = int(contagem_especiais)

        df_temp[nome_col] = pd.to_numeric(df_temp[nome_col], errors="coerce")

        if df_mestre.empty:
            df_mestre = df_temp
        else:
            df_mestre = pd.merge(df_mestre, df_temp, on="Municipio", how="outer")

        time.sleep(0.5)

    # Tratamento de ausentes:
    # NaN remanescente após coerce vem de células com códigos especiais
    # (sigilo, não disponível, não se aplica). Tratamos como 0 para fins
    # de visualização, com a ressalva documentada em METODOLOGIA.md.
    df_mestre = df_mestre.fillna(0)

    saida = os.path.join(pasta, "dados_agro_ro_master.csv")
    df_mestre.to_csv(saida, index=False)

    print("\n--- Relatório de coleta ---")
    print(f"Municípios coletados: {len(df_mestre)}")
    for col, qtd in relatorio.items():
        print(f"  {col}: {qtd} células com código especial (tratadas como 0)")
    print(f"\nArquivo salvo: {saida}")


if __name__ == "__main__":
    coletar_soja_ro()
