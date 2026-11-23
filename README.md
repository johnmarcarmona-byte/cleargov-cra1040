# 🌿 ClearGov — Plataforma de Inteligencia y Transparencia Tarifaria (CRA 1040)

**Autores:** Erica Márquez · David Antolínez ·  John Mario Carmona
**Institución:** Universidad Autónoma de Occidente (UAO)  

---

## 📋 Descripción del Proyecto
**ClearGov** es una plataforma SaaS orientada a empresas prestadoras del servicio público de aseo (**B2B**), entes territoriales/de control (**B2G**) y veedurías ciudadanas. A partir de la carga de un archivo CSV operativo, la plataforma audita el cumplimiento de la **Resolución CRA 1040**, previene sanciones regulatorias ante la SSPD, simula escenarios tarifarios y traduce información técnica en visores de datos abiertos comprensibles para el ciudadano.

---

## 🧠 Metodología CRISP-DM + Arquitectura Medallion

El proyecto integra el ciclo de vida estándar de minería de datos **CRISP-DM** con un pipeline ETL estructurado en **Arquitectura Medallion**:

| Fase CRISP-DM | Capa Medallion | Implementación en ClearGov |
| :--- | :--- | :--- |
| **1. Comprensión del Negocio** | — | Definición del Business Model Canvas, actores (B2B/B2G/Ciudadanía) y marco regulatorio (Resolución CRA 1040 y Ley 142 de 1994). |
| **2. Comprensión de los Datos** | 🥉 **Bronze** (`src/etl_bronze.py`) | Ingesta de archivos CSV crudos de los operadores, validación de esquema mínimo y registro de metadatos de trazabilidad. |
| **3. Preparación de los Datos** | 🥈 **Silver** (`src/etl_silver.py`) | Estandarización, detección de anomalías para reporte SUI (nulos, valores negativos) e imputación controlada por estrato. |
| **4. Modelado** | 🥇 **Gold** (`src/etl_gold.py`) | Motor matemático de cálculo tarifario CRA 1040 ($CR = CCS + CBL + CRT + CDF$), aplicación de subsidios/contribuciones y simulador de proyección. |
| **5. Evaluación** | 🥇 **Gold** (`src/etl_gold.py`) | Auditoría automática de desviación entre tarifa cobrada y tarifa regulatoria (semáforo de riesgo de sanción $>3\%$). |
| **6. Despliegue** | 🌐 **App Web** (`app.py`) | Aplicación interactiva desarrollada en **Streamlit + Plotly** desplegada en Streamlit Community Cloud. |

---

## 📁 Estructura del Repositorio

```text
cleargov-cra1040/
├── 01_comprension_negocio/   # Documentación del problema y alcance regulatorio
├── 02_comprension_datos/     # Diccionario de variables SUI / CRA 1040
├── 03_preparacion_datos/     # Reglas de limpieza y auditoría Silver
├── 04_modelado/              # Ecuaciones tarifarias CRA 1040 y simulación
├── 05_evaluacion/            # Métricas de cumplimiento y validación
├── 06_despliegue/            # Configuración de despliegue continuo
├── data/
│   ├── 01_bronze/            # Datos crudos ingeridos
│   ├── 02_silver/            # Datos limpios y auditados
│   └── 03_gold/              # Tablas analíticas y KPIs finales
├── src/
│   ├── generate_dataset.py   # Generador de dataset sintético realista
│   ├── etl_bronze.py         # Pipeline capa Bronze
│   ├── etl_silver.py         # Pipeline capa Silver
│   └── etl_gold.py           # Pipeline capa Gold
├── app.py                    # Interfaz web principal (Streamlit)
└── requirements.txt          # Dependencias del proyecto