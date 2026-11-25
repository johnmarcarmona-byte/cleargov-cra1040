import pandas as pd
from datetime import datetime
import os

COLUMNAS_REQUERIDAS = [
    "id_empresa", "nombre_empresa", "municipio", "departamento",
    "periodo_mes", "estrato", "suscriptores_totales",
    "toneladas_no_aprovechables", "toneladas_aprovechadas",
    "km_barrido_limpieza", "costo_comercializacion_ccs",
    "costo_barrido_cbl", "costo_recoleccion_transporte_crt",
    "costo_disposicion_final_cdf", "costo_limpieza_urbana_clus",
    "factor_subsidio_contribucion", "tarifa_cobrada_actual"
]

def procesar_bronze(ruta_csv: str, nombre_origen: str = "carga_manual.csv") -> pd.DataFrame:
    df = pd.read_csv(ruta_csv)
    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"El archivo CSV no cumple con el esquema mínimo CRA 1040. Faltan columnas: {faltantes}")
    
    df["_bronze_fecha_ingesta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["_bronze_archivo_origen"] = nombre_origen
    
    os.makedirs("data/01_bronze", exist_ok=True)
    df.to_csv("data/01_bronze/bronze_ingestado.csv", index=False, encoding="utf-8")
    return df
