import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.etl_bronze import procesar_bronze
from src.etl_silver import procesar_silver
from src.etl_gold import procesar_gold

def ejecutar_evaluacion():
    print("=== EVALUACIÓN TÉCNICA DEL PIPELINE MEDALLION Y MODELOS CRA 1040 (INCLUYE CLUS) ===")
    df_b = procesar_bronze("data/01_bronze/reporte_operador_ejemplo.csv", "test_evaluacion.csv")
    df_s = procesar_silver(df_b)
    df_g = procesar_gold(df_s)
    
    alertas_silver = int(df_s["tiene_alerta_calidad"].sum())
    assert alertas_silver == 2
    assert df_s["toneladas_no_aprovechables"].isna().sum() == 0
    assert (df_s["km_barrido_limpieza"] < 0).sum() == 0
    
    cr_check = (
        df_g["costo_comercializacion_ccs"] +
        df_g["costo_barrido_cbl"] +
        df_g["costo_recoleccion_transporte_crt"] +
        df_g["costo_disposicion_final_cdf"] +
        df_g["costo_limpieza_urbana_clus"]
    ).round(2)
    error_max_cr = np.abs(df_g["costo_referencia_cra1040"] - cr_check).max()
    assert error_max_cr < 1e-6
    
    sobrecobros = len(df_g[df_g["estado_cumplimiento_tarifario"] == "ALTO RIESGO (Sobrecobro > 3%)"])
    assert sobrecobros == 1
    
    print(f"[OK] Precisión detección anomalías Silver: 100% ({alertas_silver}/2)")
    print(f"[OK] Precisión detección sobrecobro Gold: 100% ({sobrecobros}/1)")
    print(f"[OK] Error aritmético máximo (CCS+CBL+CRT+CDF+CLUS): {error_max_cr:.8f} COP")

if __name__ == "__main__":
    ejecutar_evaluacion()
