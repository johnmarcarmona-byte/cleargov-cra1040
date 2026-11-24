# Fase 6: Despliegue y Operación Continua (Deployment)

## 1. Arquitectura de Despliegue en la Nube
La plataforma **ClearGov** opera bajo un esquema de **Integración Continua y Despliegue Continuo (CI/CD)** sin costos de infraestructura:
* **Control de Versiones:** Repositorio centralizado en GitHub (`johnmarcarmona-byte/cleargov-cra1040`, rama `main`).
* **Entorno de Ejecución:** Contenedor Linux gestionado en **Streamlit Community Cloud** con Python 3.13 y dependencias aisladas mediante `requirements.txt`.
* **URL Productiva:** `https://cleargov-cra1040-8jiowai5bj6mdvjrz5wv5u.streamlit.app/`

## 2. Flujo de Actualización (CI/CD)
1. El equipo de ingeniería realiza mejoras sobre los scripts ETL (`src/`) o la interfaz (`app.py`) en entorno local (`.venv`).
2. Se ejecutan las pruebas de validación (`py 05_evaluacion/validar_modelos.py`).
3. Al ejecutar `git push origin main`, Streamlit Community Cloud detecta automáticamente el nuevo *commit*, reconstruye el entorno si hubo cambios en `requirements.txt` y actualiza la aplicación en producción en menos de 45 segundos.

## 3. Plan de Escalabilidad Futura (Roadmap Post-MVP)
* **Persistencia Relacional / Lakehouse:** Migrar almacenamiento CSV local a **PostgreSQL / Supabase** o **AWS S3 + Parquet** para histórico multi-anual de múltiples municipios.
* **Autenticación por Roles (RBAC):** Separar vistas públicas (ciudadanía) de sesiones privadas autenticadas por NIT para cada empresa operadora.
* **Conexión API directa con SUI:** Automatizar la extracción mediante web services oficiales de la SSPD.
