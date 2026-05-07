"""
Validação de sanidade dos dados PAM-IBGE para 4 culturas de Rondônia.

Roda 4 níveis de checagem:
  1. Estrutural: 52 municípios, sem duplicatas, sem negativos, GeoJSON ↔ CSV
  2. Consistência interna: Quantidade ≈ Área × Produtividade (apenas Soja e Milho —
     PAM 1613 não publica área plantada de lavouras permanentes na mesma estrutura)
  3. Ranges plausíveis: produtividade dentro de bandas históricas para RO
  4. Coerência cruzada: Valor (R$ mil) > 0 quando Quantidade > 0

Saída:
  - Relatório no stdout
  - Exit code 0 se tudo passa, 1 se há violações (CI/GitHub Actions)

Uso:
    python validate_data.py
"""
import json
import os
import sys
import pandas as pd

# Força UTF-8 no stdout (Windows usa cp1252 por padrão e quebra com acentos/símbolos)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PASTA = os.path.dirname(__file__)
CSV = os.path.join(PASTA, "dados_agro_ro_master.csv")
GEOJSON = os.path.join(PASTA, "mapa_ro.json")

# Rondônia tem 52 municípios (IBGE — Malha Municipal 2022).
TOTAL_MUNICIPIOS_RO = 52

# Tolerância para identidade Quantidade = Área Plantada × Produtividade.
# IBGE-PAM publica Área Plantada (semeada) e Quantidade (efetivamente colhida).
# Quando há perda de safra (chuva, doença), Quantidade < Área Plantada × Produtividade.
# 12% cobre perdas típicas em RO sem mascarar erros reais.
TOLERANCIA_CONSISTENCIA = 0.12

# Produção mínima para validar consistência por % de desvio. Abaixo disso (residual,
# subsistência, sigilo estatístico próximo de zero), arredondamento gera grandes
# desvios percentuais sem significado analítico.
PRODUCAO_MINIMA_VALIDAVEL_T = 500

# Ranges plausíveis para Rondônia (calibrados pela média histórica IBGE/CONAB/Embrapa).
# Cobrem ambos os regimes: comercial mecanizado (Cone Sul) e familiar (Zona da Mata).
RANGES_PRODUTIVIDADE_KG_HA = {
    "Soja":  {"min": 2500, "max": 4500},   # 2,5 a 4,5 t/ha
    "Milho": {"min": 1500, "max": 6500},   # 1,5 a 6,5 t/ha (subsistência + safrinha comercial)
    "Cafe":  {"min": 800,  "max": 5000},   # 0,8 a 5 t/ha (conilon RO; ES bate ~5 t/ha topo)
    "Cacau": {"min": 300,  "max": 2500},   # 0,3 a 2,5 t/ha (RO ainda em consolidação produtiva)
}

CULTURAS_COM_AREA = ["Soja", "Milho"]  # PAM 1613 (lavouras permanentes) não tem área plantada
CULTURAS_TODAS = list(RANGES_PRODUTIVIDADE_KG_HA.keys())

# Colunas obrigatórias (todas as variáveis × 4 culturas, exceto área para permanentes)
COLUNAS_OBRIGATORIAS = ["Municipio"]
for c in CULTURAS_TODAS:
    COLUNAS_OBRIGATORIAS += [f"{c}_Qtd_T", f"{c}_Valor_Mil", f"{c}_Prod_KgHa"]
for c in CULTURAS_COM_AREA:
    COLUNAS_OBRIGATORIAS.append(f"{c}_AreaPlant_Ha")


def validar_estrutura(df, geo):
    erros = []

    for col in COLUNAS_OBRIGATORIAS:
        if col not in df.columns:
            erros.append(f"Coluna ausente: {col}")

    if len(df) != TOTAL_MUNICIPIOS_RO:
        erros.append(f"Cobertura municipal: {len(df)} (esperado {TOTAL_MUNICIPIOS_RO})")

    if df["Municipio"].duplicated().any():
        n = int(df["Municipio"].duplicated().sum())
        erros.append(f"Municípios duplicados: {n}")

    cols_numericas = [c for c in df.columns if c != "Municipio"]
    for c in cols_numericas:
        if c in df.columns and (df[c] < 0).any():
            n = int((df[c] < 0).sum())
            erros.append(f"Coluna {c}: {n} valor(es) negativo(s)")

    nomes_geo = {f["properties"]["name"] for f in geo["features"]}
    faltam_no_geo = set(df["Municipio"]) - nomes_geo
    if faltam_no_geo:
        erros.append(f"Municípios do CSV ausentes no GeoJSON: {sorted(faltam_no_geo)}")

    return erros


def validar_consistencia(df, cultura):
    """Quantidade ≈ Área Plantada × Produtividade — apenas para culturas com área."""
    erros = []
    qtd_col = f"{cultura}_Qtd_T"
    area_col = f"{cultura}_AreaPlant_Ha"
    prod_col = f"{cultura}_Prod_KgHa"

    for _, r in df.iterrows():
        qtd, area, prod = r[qtd_col], r[area_col], r[prod_col]
        if area > 0 and prod > 0 and qtd >= PRODUCAO_MINIMA_VALIDAVEL_T:
            esperado = area * prod / 1000
            desvio = abs(qtd - esperado) / esperado
            if desvio > TOLERANCIA_CONSISTENCIA:
                erros.append(
                    f"  {r['Municipio']:30s} {cultura}: "
                    f"qtd={qtd:>9,.0f} t · esperado={esperado:>9,.0f} t · "
                    f"desvio {desvio*100:+.1f}%"
                )
    return erros


def validar_produtividade(df, cultura):
    """Produtividade dentro do range plausível para Rondônia."""
    erros = []
    prod_col = f"{cultura}_Prod_KgHa"
    qtd_col = f"{cultura}_Qtd_T"
    minimo = RANGES_PRODUTIVIDADE_KG_HA[cultura]["min"]
    maximo = RANGES_PRODUTIVIDADE_KG_HA[cultura]["max"]

    for _, r in df.iterrows():
        prod = r[prod_col]
        # Ignora produção residual: produtividade calculada sobre amostra mínima
        # (< 50 t total) é estatisticamente instável.
        if prod > 0 and r[qtd_col] >= 50 and (prod < minimo or prod > maximo):
            erros.append(
                f"  {r['Municipio']:30s} {cultura}: "
                f"produtividade {prod:>5,.0f} kg/ha "
                f"fora do range ({minimo:,}–{maximo:,} kg/ha)"
            )
    return erros


def validar_coerencia_cruzada(df, cultura):
    """Valor > 0 ↔ Quantidade > 0 (não pode haver produção sem valor monetário)."""
    erros = []
    qtd_col = f"{cultura}_Qtd_T"
    val_col = f"{cultura}_Valor_Mil"

    qtd_sem_valor = df[(df[qtd_col] > 0) & (df[val_col] == 0)]
    for _, r in qtd_sem_valor.iterrows():
        erros.append(
            f"  {r['Municipio']:30s} {cultura}: "
            f"qtd={r[qtd_col]:,.0f} t mas Valor = 0 (incoerente — produção sem registro de valor)"
        )

    val_sem_qtd = df[(df[qtd_col] == 0) & (df[val_col] > 0)]
    for _, r in val_sem_qtd.iterrows():
        erros.append(
            f"  {r['Municipio']:30s} {cultura}: "
            f"Valor R$ {r[val_col]:,.0f} mil mas Qtd = 0 (incoerente — valor sem produção)"
        )
    return erros


def main():
    print("=" * 70)
    print(f"VALIDAÇÃO DE SANIDADE — {os.path.basename(CSV)}")
    print("=" * 70)

    try:
        df = pd.read_csv(CSV)
    except FileNotFoundError:
        print(f"\nERRO: arquivo {CSV} não encontrado. Rode `python coleta_geral.py` primeiro.")
        return 1

    try:
        with open(GEOJSON, encoding="utf-8") as f:
            geo = json.load(f)
    except FileNotFoundError:
        print(f"\nERRO: arquivo {GEOJSON} não encontrado.")
        return 1

    print(f"\nMunicípios carregados: {len(df)}")
    print(f"Tolerância consistência: {TOLERANCIA_CONSISTENCIA*100:.0f}%")
    print("Ranges produtividade (kg/ha):")
    for c, r in RANGES_PRODUTIVIDADE_KG_HA.items():
        print(f"  {c:6s} {r['min']:>5,}–{r['max']:>5,}")

    todos_erros = []

    print("\n--- 1. Sanidade estrutural ---")
    erros = validar_estrutura(df, geo)
    if erros:
        print(f"  {len(erros)} violação(ões)")
        for e in erros:
            print(f"  {e}")
        todos_erros.extend(erros)
    else:
        print("  OK")

    print("\n--- 2. Consistência interna (Qtd ≈ Área × Produtividade) ---")
    print("    [apenas Soja e Milho — PAM lavouras permanentes não publica área plantada]")
    for cultura in CULTURAS_COM_AREA:
        erros = validar_consistencia(df, cultura)
        if erros:
            print(f"\n  {cultura}: {len(erros)} violação(ões)")
            for e in erros:
                print(e)
            todos_erros.extend(erros)
        else:
            print(f"  {cultura}: OK")

    print("\n--- 3. Produtividade dentro do range esperado ---")
    for cultura in CULTURAS_TODAS:
        erros = validar_produtividade(df, cultura)
        if erros:
            print(f"\n  {cultura}: {len(erros)} violação(ões)")
            for e in erros:
                print(e)
            todos_erros.extend(erros)
        else:
            print(f"  {cultura}: OK")

    print("\n--- 4. Coerência cruzada (Quantidade ↔ Valor) ---")
    for cultura in CULTURAS_TODAS:
        erros = validar_coerencia_cruzada(df, cultura)
        if erros:
            print(f"\n  {cultura}: {len(erros)} violação(ões)")
            for e in erros:
                print(e)
            todos_erros.extend(erros)
        else:
            print(f"  {cultura}: OK")

    print("\n" + "=" * 70)
    if todos_erros:
        print(f"REPROVADO: {len(todos_erros)} violação(ões) encontradas")
        print("=" * 70)
        return 1
    print("APROVADO: todos os checks passaram")
    print(f"  Produção total de soja: {df['Soja_Qtd_T'].sum():,.0f} t")
    print(f"  Produção total de milho: {df['Milho_Qtd_T'].sum():,.0f} t")
    print(f"  Produção total de café: {df['Cafe_Qtd_T'].sum():,.0f} t")
    print(f"  Produção total de cacau: {df['Cacau_Qtd_T'].sum():,.0f} t")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
