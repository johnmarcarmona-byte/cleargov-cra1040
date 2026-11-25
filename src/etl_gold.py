import pandas as pd
import numpy as np
import os

def procesar_gold(df_silver: pd.DataFrame) -> pd.DataFrame:
    df = df_silver.copy()
    
    df["costo_referencia_cra1040"] = (
        df["costo_comercializacion_ccs"] +
        df["costo_barrido_cbl"] +
        df["costo_recoleccion_transporte_crt"] +
        df["costo_disposicion_final_cdf"] +
        df["costo_limpieza_urbana_clus"]
    ).round(2)
    
    df["tarifa_regulatoria_calculada"] = (
        df["costo_referencia_cra1040"] * (1 + df["factor_subsidio_contribucion"])
    ).round(2)
    
    df["desviacion_tarifaria_pesos"] = (df["tarifa_cobrada_actual"] - df["tarifa_regulatoria_calculada"]).round(2)
    df["desviacion_porcentual"] = (
        (df["desviacion_tarifaria_pesos"] / df["tarifa_regulatoria_calculada"]) * 100
    ).round(2)
    
    def clasificar_riesgo(desv):
        if desv > 3.0:
            return "ALTO RIESGO (Sobrecobro > 3%)"
        elif desv < -3.0:
            return "RIESGO FINANCIERO (Subcobro > 3%)"
        else:
            return "CUMPLIMIENTO ÓPTIMO"
            
    df["estado_cumplimiento_tarifario"] = df["desviacion_porcentual"].apply(clasificar_riesgo)

    # Diagnóstico unificado de intervención y exposición sancionatoria (Ley 142 / SUI)
    def generar_diagnostico_sancion(row):
        hallazgos = []
        if row["desviacion_porcentual"] > 3.0:
            hallazgos.append(
                f"INTERVENCIÓN URGENTE: Sobrecobro del +{row['desviacion_porcentual']:.2f}% sobre tope CRA 1040. "
                "Exposición a devolución de cobros y multa SSPD hasta 2.000 SMLMV (Art. 81 Ley 142)."
            )
        elif row["desviacion_porcentual"] < -3.0:
            hallazgos.append(
                f"REVISIÓN FINANCIERA: Subcobro del {row['desviacion_porcentual']:.2f}% frente a tarifa regulada. "
                "Riesgo de déficit operativo y glosa en cierre financiero SUI."
            )
        
        if row["tiene_alerta_calidad"]:
            hallazgos.append(
                f"CORREGIR ANTES DE CARGUE SUI: {row['auditoria_calidad_sui']}. "
                "Reportar inconsistencias al SUI acarrea sanción SSPD hasta 2.000 SMLMV (Art. 81 Ley 142)."
            )
            
        return " | ".join(hallazgos) if hallazgos else "Sin hallazgos regulatorios"

    df["diagnostico_y_exposicion_sspd"] = df.apply(generar_diagnostico_sancion, axis=1)
    
    total_ton = df["toneladas_no_aprovechables"] + df["toneladas_aprovechadas"]
    df["tasa_aprovechamiento_pct"] = np.where(
        total_ton > 0, ((df["toneladas_aprovechadas"] / total_ton) * 100).round(2), 0
    )
    df["recaudo_mensual_estimado"] = (df["tarifa_cobrada_actual"] * df["suscriptores_totales"]).round(0)
    
    os.makedirs("data/03_gold", exist_ok=True)
    df.to_csv("data/03_gold/gold_analitico.csv", index=False, encoding="utf-8")
    return df
