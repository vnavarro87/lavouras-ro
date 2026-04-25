"""
Validações de integridade do dataset de soja em Rondônia.
Roda como script: `python validate_data.py`
Falha (sai com erro) se alguma asserção quebrar.
"""
import os
import json
import sys
import pandas as pd

PASTA = os.path.dirname(__file__)
CSV = os.path.join(PASTA, "dados_agro_ro_master.csv")
GEOJSON = os.path.join(PASTA, "mapa_ro.json")

COLUNAS_OBRIGATORIAS = [
    "Municipio",
    "Soja_Qtd_T",
    "Soja_Valor_Mil",
    "Soja_Prod_KgHa",
    "Soja_AreaPlant_Ha",
]

# Rondônia tem 52 municípios (IBGE 2022).
TOTAL_MUNICIPIOS_RO = 52


def main():
    erros = []

    df = pd.read_csv(CSV)

    for col in COLUNAS_OBRIGATORIAS:
        if col not in df.columns:
            erros.append(f"Coluna ausente: {col}")

    if len(df) != TOTAL_MUNICIPIOS_RO:
        erros.append(
            f"Número de municípios inesperado: {len(df)} (esperado {TOTAL_MUNICIPIOS_RO})"
        )

    if df["Municipio"].duplicated().any():
        erros.append("Há municípios duplicados no dataset")

    for col in COLUNAS_OBRIGATORIAS[1:]:
        if col in df.columns and (df[col] < 0).any():
            erros.append(f"Valores negativos encontrados em {col}")

    with open(GEOJSON, encoding="utf-8") as f:
        geo = json.load(f)
    nomes_geo = {f["properties"]["name"] for f in geo["features"]}
    nomes_csv = set(df["Municipio"])
    faltam_no_geo = nomes_csv - nomes_geo
    if faltam_no_geo:
        erros.append(f"Municípios do CSV ausentes no GeoJSON: {faltam_no_geo}")

    if erros:
        print("VALIDAÇÃO FALHOU:")
        for e in erros:
            print(f"  - {e}")
        sys.exit(1)

    print("Validação OK.")
    print(f"  Municípios: {len(df)}")
    print(f"  Produção total de soja: {df['Soja_Qtd_T'].sum():,.0f} t")
    print(f"  Área plantada total: {df['Soja_AreaPlant_Ha'].sum():,.0f} ha")


if __name__ == "__main__":
    main()
