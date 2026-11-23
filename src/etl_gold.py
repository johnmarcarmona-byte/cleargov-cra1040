import pandas as pd
import numpy as np
import os

def procesar_gold(df_silver):
    df = df_silver.copy()
    
    # 1. Cálculo de Costo de Referencia CRA 1040 (Costo pleno sin subsidio)
    df["costo_referencia_cra1040"] = (
        df["costo_comercializacion_ccs"] +
        df["costo_barrido_cbl"] +
        df["costo_recoleccion_transporte_crt"] +
        df["costo_disposicion_final_cdf"]
    ).round(2)
    
    # 2. Tarifa Teórica Regulatoria (aplicando factor de subsidio o contribución)
    df["tarifa_regulatoria_calculada"] = (
        df["costo_referencia_cra1040"] * (1 + df["factor_subsidio_contribucion"])
    ).round(2)
    
    # 3. Evaluación de Cumplimiento Tarifario (Auditoría anti-sanciones)
    df["diferencia_tarifa_cop"] = (df["tarifa_cobrada_actual"] - df["tarifa_regulatoria_calculada"]).round(2)
    df["desviacion_porcentual"] = ((df["diferencia_tarifa_cop"] / df["tarifa_regulatoria_calculada"]) * 100).round(2)
    
    def clasificar_riesgo(desv):
        if desv > 3.0:
            return "ALTO RIESGO (Sobrecobro > 3%)"
        elif desv < -3.0:
            return "RIESGO FINANCIERO (Subcobro > 3%)"
        return "CUMPLIMIENTO ÓPTIMO"
        
    df["estado_cumplimiento_tarifario"] = df["desviacion_porcentual"].apply(clasificar_riesgo)
    
    # 4. Indicadores de Datos Abiertos (KPIs ciudadanos y B2G)
    df["recaudo_mensual_estimado"] = (df["tarifa_cobrada_actual"] * df["suscriptores_totales"]).round(0)
    df["tasa_aprovechamiento_pct"] = (
        (df["toneladas_aprovechadas"] / (df["toneladas_aprovechables" if "toneladas_aprovechables" in df.columns else "toneladas_aprovechadas"] + df["toneladas_no_aprovechables"])) * 100
    ).round(2)
    
    os.makedirs("data/03_gold", exist_ok=True)
    ruta_salida = "data/03_gold/gold_analitica_tarifaria.csv"
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    return df

if __name__ == "__main__":
    df_s = pd.read_csv("data/02_silver/silver_datos_limpios.csv")
    df_g = procesar_gold(df_s)
    print(f"[GOLD] Tablas analíticas generadas. Distribución de cumplimiento:\n{df_g['estado_cumplimiento_tarifario'].value_counts()}")