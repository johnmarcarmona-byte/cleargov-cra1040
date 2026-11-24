# Fase 3: Preparación de los Datos (Data Preparation - Capas Bronze y Silver)

## 1. Arquitectura de Ingesta y Trazabilidad (Capa Bronze)
Implementada en `src/etl_bronze.py`:
* **Validación de Esquema (Schema Enforcement):** Verifica la presencia obligatoria de las 16 columnas regulatorias antes de procesar. Si falta alguna columna, detiene la ejecución y notifica el error estructural.
* **Metadatos de Auditoría:** Inyecta `_bronze_fecha_ingesta` (timestamp ISO) y `_bronze_archivo_origen` para garantizar inmutabilidad y trazabilidad forense del dato crudo.

## 2. Reglas de Limpieza y Calidad (Capa Silver)
Implementada en `src/etl_silver.py`:
1. **Estandarización Léxica:** Eliminación de espacios en blanco (`strip()`) en `estrato` y normalización a formato título (`title()`) en `municipio` para evitar duplicidad en agrupaciones.
2. **Motor de Auditoría Pre-SUI (`auditoria_calidad_sui`):** Antes de corregir los datos, cada fila es evaluada contra tres reglas regulatorias:
   * *Regla R1 (Toneladas):* `toneladas_no_aprovechables` nula o $< 0 \rightarrow$ Alerta *"Dato inválido/nulo en toneladas no aprovechables (Riesgo reporte SUI)"*.
   * *Regla R2 (Barrido):* `km_barrido_limpieza` nula o $< 0 \rightarrow$ Alerta *"Kilómetros de barrido negativos o nulos"*.
   * *Regla R3 (Suscriptores):* `suscriptores_totales` $\le 0 \rightarrow$ Alerta *"Número de suscriptores inválido"*.
3. **Saneamiento e Imputación Robusta:**
   * Conversión forzada a tipo numérico (`pd.to_numeric(..., errors="coerce")`).
   * Reemplazo de valores operativos negativos por `NaN`.
   * **Imputación Estratificada por Mediana:** Los valores faltantes se imputan utilizando la mediana agrupada por `estrato` (`groupby("estrato").transform("median")`). Se selecciona la **mediana** sobre la media para evitar sesgos producidos por valores atípicos extremos (outliers).
