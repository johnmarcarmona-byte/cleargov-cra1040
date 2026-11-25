import pandas as pd
import numpy as np
import os

def generar_datos_ejemplo():
    np.random.seed(42)
    os.makedirs("data/01_bronze", exist_ok=True)
    
    empresas = [
        {"id": "900123456", "nombre": "Aseos del Oriente S.A. E.S.P.", "municipio": "Rionegro", "depto": "Antioquia"},
        {"id": "900987654", "nombre": "Servia Ambiental del Sur E.S.P.", "municipio": "Pasto", "depto": "Nariño"}
    ]
    
    estratos = [
        ("Estrato 1", -0.50, 1200),
        ("Estrato 2", -0.35, 1800),
        ("Estrato 3", -0.15, 950),
        ("Estrato 4",  0.00, 400),
        ("Estrato 5",  0.50, 180),
        ("Estrato 6",  0.60, 90),
        ("Comercial",  0.50, 220),
        ("Oficial",    0.00, 45)
    ]
    
    meses = [f"2025-{m:02d}" for m in range(1, 13)]
    registros = []
    
    for emp in empresas:
        for mes in meses:
            for est, factor_sub, susc_base in estratos:
                suscriptores = int(susc_base * np.random.uniform(0.98, 1.03))
                ton_no_aprov = round(suscriptores * np.random.uniform(0.035, 0.055), 2)
                ton_aprov = round(ton_no_aprov * np.random.uniform(0.08, 0.22), 2)
                km_barrido = round(suscriptores * np.random.uniform(0.015, 0.025), 2)
                
                ccs = round(np.random.uniform(2800, 3200), 2)
                cbl = round(np.random.uniform(4100, 4800), 2)
                crt = round(np.random.uniform(7500, 8600), 2)
                cdf = round(np.random.uniform(5200, 6100), 2)
                clus = round(np.random.uniform(1600, 2100), 2)
                
                costo_ref = ccs + cbl + crt + cdf + clus
                tarifa_reg = round(costo_ref * (1 + factor_sub), 2)
                tarifa_cobrada = round(tarifa_reg * np.random.uniform(0.99, 1.01), 2)
                
                registros.append({
                    "id_empresa": emp["id"],
                    "nombre_empresa": emp["nombre"],
                    "municipio": emp["municipio"],
                    "departamento": emp["depto"],
                    "periodo_mes": mes,
                    "estrato": est,
                    "suscriptores_totales": suscriptores,
                    "toneladas_no_aprovechables": ton_no_aprov,
                    "toneladas_aprovechadas": ton_aprov,
                    "km_barrido_limpieza": km_barrido,
                    "costo_comercializacion_ccs": ccs,
                    "costo_barrido_cbl": cbl,
                    "costo_recoleccion_transporte_crt": crt,
                    "costo_disposicion_final_cdf": cdf,
                    "costo_limpieza_urbana_clus": clus,
                    "factor_subsidio_contribucion": factor_sub,
                    "tarifa_cobrada_actual": tarifa_cobrada
                })
                
    df = pd.DataFrame(registros)
    df.loc[5, "tarifa_cobrada_actual"] = round(df.loc[5, "tarifa_cobrada_actual"] * 1.25, 2)
    df.loc[12, "toneladas_no_aprovechables"] = np.nan
    df.loc[20, "km_barrido_limpieza"] = -15.0
    
    ruta_salida = "data/01_bronze/reporte_operador_ejemplo.csv"
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"Dataset actualizado con CLUS: {len(df)} registros.")

if __name__ == "__main__":
    generar_datos_ejemplo()
