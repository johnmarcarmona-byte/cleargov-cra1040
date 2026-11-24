import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.etl_bronze import procesar_bronze
from src.etl_silver import procesar_silver
from src.etl_gold import procesar_gold

def ejecutar_evaluacion():
    print("=== EVALUACIÓN TÉCNICA DEL PIPELINE MEDALLION Y MODELOS CRA 1040 ===")
    
    # 1. Ejecutar flujo completo sobre dataset con anomalías conocidas
    df_b = procesar_bronze("data/01_bronze/reporte_operador_ejemplo.csv", "test_evaluacion.csv")
    df_s = procesar_silver(df_b)
    df_g = procesar_gold(df_s)
    
    # 2. Validación de calidad Silver (2 anomalías inyectadas: fila 12 nula y fila 20 negativa)
    alertas_silver = int(df_s["tiene_alerta_calidad"].sum())
    assert alertas_silver == 2, f"Se esperaban 2 alertas en Silver, se encontraron {alertas_silver}"
    assert df_s["toneladas_no_aprovechables"].isna().sum() == 0, "Persisten nulos tras imputación Silver"
    assert (df_s["km_barrido_limpieza"] < 0).sum() == 0, "Persisten valores negativos tras limpieza Silver"
    
    # 3. Validación matemática de tarifas Gold
    cr_check = (
        df_g["costo_comercializacion_ccs"] +
        df_g["costo_barrido_cbl"] +
        df_g["costo_recoleccion_transporte_crt"] +
        df_g["costo_disposicion_final_cdf"]
    ).round(2)
    error_max_cr = np.abs(df_g["costo_referencia_cra1040"] - cr_check).max()
    assert error_max_cr < 1e-6, f"Error de precisión en Costo de Referencia: {error_max_cr}"
    
    # 4. Validación de detección de sobrecobro (1 anomalía inyectada en fila 5: +25%)
    sobrecobros = len(df_g[df_g["estado_cumplimiento_tarifario"] == "ALTO RIESGO (Sobrecobro > 3%)"])
    assert sobrecobros == 1, f"Se esperaba 1 alerta de sobrecobro, se encontraron {sobrecobros}"
    
    print(f"[OK] Precisión detección anomalías Silver (Recall): 100% ({alertas_silver}/2 detectadas)")
    print(f"[OK] Precisión detección sobrecobro Gold (Recall): 100% ({sobrecobros}/1 detectado)")
    print(f"[OK] Error aritmético máximo en ecuaciones CRA 1040: {error_max_cr:.8f} COP")
    print("[OK] Todas las pruebas de evaluación superadas exitosamente.")

if __name__ == "__main__":
    ejecutar_evaluacion()
