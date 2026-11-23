import pandas as pd
import numpy as np
import os

def procesar_silver(df_bronze):
    df = df_bronze.copy()
    
    # 1. Estandarización de texto
    df["estrato"] = df["estrato"].str.strip()
    df["municipio"] = df["municipio"].str.strip().str.title()
    
    # 2. Auditoría de calidad y detección de alertas regulatorias (Riesgo SSPD)
    alertas = []
    for idx, row in df.iterrows():
        mensajes = []
        if pd.isna(row["toneladas_no_aprovechables"]) or row["toneladas_no_aprovechables"] < 0:
            mensajes.append("Dato inválido/nulo en toneladas no aprovechables (Riesgo reporte SUI)")
        if pd.isna(row["km_barrido_limpieza"]) or row["km_barrido_limpieza"] < 0:
            mensajes.append("Kilómetros de barrido negativos o nulos")
        if row["suscriptores_totales"] <= 0:
            mensajes.append("Número de suscriptores inválido")
            
        alertas.append(" | ".join(mensajes) if mensajes else "OK - Cumple validación")
        
    df["auditoria_calidad_sui"] = alertas
    df["tiene_alerta_calidad"] = df["auditoria_calidad_sui"] != "OK - Cumple validación"
    
    # 3. Limpieza e imputación controlada para permitir el cálculo tarifario
    cols_numericas = [
        "suscriptores_totales", "toneladas_no_aprovechables", "toneladas_aprovechadas",
        "km_barrido_limpieza", "costo_comercializacion_ccs", "costo_barrido_cbl",
        "costo_recoleccion_transporte_crt", "costo_disposicion_final_cdf",
        "factor_subsidio_contribucion", "tarifa_cobrada_actual"
    ]
    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Reemplazar valores negativos operativos por NaN y luego imputar con la mediana del estrato
        if col != "factor_subsidio_contribucion":
            df.loc[df[col] < 0, col] = np.nan
        df[col] = df[col].fillna(df.groupby("estrato")[col].transform("median"))
        
    os.makedirs("data/02_silver", exist_ok=True)
    ruta_salida = "data/02_silver/silver_datos_limpios.csv"
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    return df

if __name__ == "__main__":
    df_b = pd.read_csv("data/01_bronze/bronze_datos_crudos.csv")
    df_s = procesar_silver(df_b)
    print(f"[SILVER] Limpieza y auditoría completadas. Alertas detectadas: {df_s['tiene_alerta_calidad'].sum()}")