import pandas as pd
import numpy as np
import os

def generar_datos_cra1040():
    np.random.seed(42)
    
    empresas = [
        {"id_empresa": "900123456", "nombre_empresa": "Aseos del Oriente S.A. E.S.P.", "municipio": "Rionegro", "departamento": "Antioquia"},
        {"id_empresa": "900987654", "nombre_empresa": "Aguas y Aseo del Valle E.S.P.", "municipio": "Marinilla", "departamento": "Antioquia"}
    ]
    
    periodos = pd.date_range(start="2025-01-01", periods=12, freq="MS").strftime("%Y-%m").tolist()
    
    estratos = [
        {"estrato": "Estrato 1", "factor_subsidio": -0.50, "suscriptores_base": 1200},
        {"estrato": "Estrato 2", "factor_subsidio": -0.30, "suscriptores_base": 1800},
        {"estrato": "Estrato 3", "factor_subsidio": -0.10, "suscriptores_base": 950},
        {"estrato": "Estrato 4", "factor_subsidio": 0.00,  "suscriptores_base": 400},
        {"estrato": "Estrato 5", "factor_subsidio": 0.50,  "suscriptores_base": 150},
        {"estrato": "Estrato 6", "factor_subsidio": 0.60,  "suscriptores_base": 80},
        {"estrato": "Comercial", "factor_subsidio": 0.50,  "suscriptores_base": 320},
        {"estrato": "Oficial",   "factor_subsidio": 0.00,  "suscriptores_base": 45},
    ]
    
    registros = []
    
    for emp in empresas:
        for periodo in periodos:
            for est in estratos:
                suscriptores = int(est["suscriptores_base"] * np.random.uniform(0.98, 1.03))
                ton_no_aprov = round(suscriptores * np.random.uniform(0.035, 0.048), 2)
                ton_aprov = round(ton_no_aprov * np.random.uniform(0.08, 0.18), 2)
                km_barrido = round(suscriptores * np.random.uniform(0.015, 0.025), 2)
                
                # Costos unitarios base CRA 1040 ($ COP por suscriptor/mes)
                ccs = round(np.random.uniform(3200, 3600), 2)  # Comercialización
                cbl = round(np.random.uniform(4100, 4800), 2)  # Barrido y Limpieza
                crt = round(np.random.uniform(8500, 9800), 2)  # Recolección y Transporte
                cdf = round(np.random.uniform(3800, 4500), 2)  # Disposición Final
                
                # Tarifa de referencia técnica (CRT + CDF + CBL + CCS) * (1 + factor_subsidio)
                tarifa_tecnica = (ccs + cbl + crt + cdf) * (1 + est["factor_subsidio"])
                
                # Simulamos lo que realmente cobró la empresa (normalmente muy cerca de la técnica)
                tarifa_cobrada = round(tarifa_tecnica * np.random.uniform(0.99, 1.01), 2)
                
                registros.append({
                    "id_empresa": emp["id_empresa"],
                    "nombre_empresa": emp["nombre_empresa"],
                    "municipio": emp["municipio"],
                    "departamento": emp["departamento"],
                    "periodo_mes": periodo,
                    "estrato": est["estrato"],
                    "suscriptores_totales": suscriptores,
                    "toneladas_no_aprovechables": ton_no_aprov,
                    "toneladas_aprovechadas": ton_aprov,
                    "km_barrido_limpieza": km_barrido,
                    "costo_comercializacion_ccs": ccs,
                    "costo_barrido_cbl": cbl,
                    "costo_recoleccion_transporte_crt": crt,
                    "costo_disposicion_final_cdf": cdf,
                    "factor_subsidio_contribucion": est["factor_subsidio"],
                    "tarifa_cobrada_actual": tarifa_cobrada
                })
                
    df = pd.DataFrame(registros)
    
    # Inyectar anomalías intencionales (para probar auditoría CRA 1040 en capa Silver)
    df.loc[5, "tarifa_cobrada_actual"] = df.loc[5, "tarifa_cobrada_actual"] * 1.25  # Sobrecobro del 25% (Riesgo sanción SSPD)
    df.loc[12, "toneladas_no_aprovechables"] = np.nan  # Dato faltante para reporte SUI
    df.loc[20, "km_barrido_limpieza"] = -15.0  # Dato negativo erróneo
    
    os.makedirs("data/01_bronze", exist_ok=True)
    ruta_salida = "data/01_bronze/reporte_operador_ejemplo.csv"
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"Dataset generado exitosamente en: {ruta_salida} ({len(df)} registros)")

if __name__ == "__main__":
    generar_datos_cra1040()