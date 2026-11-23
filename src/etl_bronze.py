import pandas as pd
from datetime import datetime
import os

COLUMNAS_REQUERIDAS = [
    "id_empresa", "nombre_empresa", "municipio", "departamento",
    "periodo_mes", "estrato", "suscriptores_totales",
    "toneladas_no_aprovechables", "toneladas_aprovechadas",
    "km_barrido_limpieza", "costo_comercializacion_ccs",
    "costo_barrido_cbl", "costo_recoleccion_transporte_crt",
    "costo_disposicion_final_cdf", "factor_subsidio_contribucion",
    "tarifa_cobrada_actual"
]

def procesar_bronze(ruta_csv_entrada, nombre_archivo="carga_manual.csv"):
    df = pd.read_csv(ruta_csv_entrada)
    
    # Validar esquema mínimo
    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"El CSV no cumple el formato CRA 1040. Faltan columnas: {faltantes}")
    
    # Agregar trazabilidad Medallion (Metadatos de ingesta)
    df_bronze = df.copy()
    df_bronze["_bronze_fecha_ingesta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_bronze["_bronze_archivo_origen"] = nombre_archivo
    
    os.makedirs("data/01_bronze", exist_ok=True)
    ruta_salida = "data/01_bronze/bronze_datos_crudos.csv"
    df_bronze.to_csv(ruta_salida, index=False, encoding="utf-8")
    return df_bronze

if __name__ == "__main__":
    df_b = procesar_bronze("data/01_bronze/reporte_operador_ejemplo.csv", "reporte_operador_ejemplo.csv")
    print(f"[BRONZE] Ingesta completada: {len(df_b)} registros guardados.")