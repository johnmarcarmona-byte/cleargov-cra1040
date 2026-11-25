import pandas as pd
import numpy as np
import os

def procesar_silver(df_bronze: pd.DataFrame) -> pd.DataFrame:
    df = df_bronze.copy()
    
    df["estrato"] = df["estrato"].astype(str).str.strip()
    df["municipio"] = df["municipio"].astype(str).str.strip().str.title()
    
    cols_numericas = [
        "suscriptores_totales", "toneladas_no_aprovechables",
        "toneladas_aprovechadas", "km_barrido_limpieza",
        "costo_comercializacion_ccs", "costo_barrido_cbl",
        "costo_recoleccion_transporte_crt", "costo_disposicion_final_cdf",
        "costo_limpieza_urbana_clus", "factor_subsidio_contribucion",
        "tarifa_cobrada_actual"
    ]
    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    alertas = []
    for _, row in df.iterrows():
        motivos = []
        if pd.isna(row["toneladas_no_aprovechables"]) or row["toneladas_no_aprovechables"] < 0:
            motivos.append("Dato inválido/nulo en toneladas no aprovechables (Riesgo reporte SUI)")
        if pd.isna(row["km_barrido_limpieza"]) or row["km_barrido_limpieza"] < 0:
            motivos.append("Kilómetros de barrido negativos o nulos")
        if pd.isna(row["suscriptores_totales"]) or row["suscriptores_totales"] <= 0:
            motivos.append("Número de suscriptores inválido")
        alertas.append(" | ".join(motivos) if motivos else "OK")
        
    df["auditoria_calidad_sui"] = alertas
    df["tiene_alerta_calidad"] = df["auditoria_calidad_sui"] != "OK"
    
    cols_positivas = [
        "toneladas_no_aprovechables", "toneladas_aprovechadas",
        "km_barrido_limpieza", "costo_comercializacion_ccs",
        "costo_barrido_cbl", "costo_recoleccion_transporte_crt",
        "costo_disposicion_final_cdf", "costo_limpieza_urbana_clus"
    ]
    for col in cols_positivas:
        df.loc[df[col] < 0, col] = np.nan
        df[col] = df[col].fillna(df.groupby("estrato")[col].transform("median"))
        
    os.makedirs("data/02_silver", exist_ok=True)
    df.to_csv("data/02_silver/silver_limpio.csv", index=False, encoding="utf-8")
    return df
