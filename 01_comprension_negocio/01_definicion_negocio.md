# Fase 1: Comprensión del Negocio (Business Understanding)

## 1. Contexto Regulatorio y Problemática
En Colombia, las empresas prestadoras del servicio público domiciliario de aseo están sujetas al régimen de regulación económica expedido por la **Comisión de Regulación de Agua Potable y Saneamiento Básico (CRA)** y a la inspección, vigilancia y control de la **Superintendencia de Servicios Públicos Domiciliarios (SSPD)** bajo la **Ley 142 de 1994** (Art. 81: régimen sancionatorio con multas de hasta 2.000 SMLMV).

Con la entrada en vigencia de los marcos tarifarios de la **Resolución CRA 1040** para pequeños prestadores (municipios con menos de 5.000 suscriptores), se identifican dos brechas críticas:
1. **Riesgo Operativo y Jurídico (B2B):** Más del 65% de los pequeños operadores calculan sus tarifas en hojas de cálculo manuales sin validación automatizada de esquemas del Sistema Único de Información (SUI), exponiéndose a sobrecobros (>3%), subcobros que afectan su sostenibilidad financiera y sanciones por inconsistencias en reportes.
2. **Asimetría de Información (B2G y Ciudadanía):** Los entes territoriales, veedurías y suscriptores reciben pliegos tarifarios complejos sin trazabilidad comprensible sobre cómo se compone su factura ni cómo aplican los subsidios y contribuciones solidarias.

## 2. Objetivos del Proyecto
* **Objetivo de Negocio:** Proveer una plataforma SaaS (**ClearGov**) que automatice la auditoría tarifaria bajo la Resolución CRA 1040 y publique portales de datos abiertos en tiempo real a partir de un archivo CSV operativo.
* **Objetivos de Ingeniería y Ciencia de Datos:**
  1. Implementar un pipeline ETL bajo **Arquitectura Medallion** (Bronze → Silver → Gold) que garantice trazabilidad, limpieza e imputación controlada de datos operativos.
  2. Desarrollar un motor determinístico de cálculo tarifario y detección de anomalías regulatorias (umbral de desviación $\pm 3\%$).
  3. Construir un simulador de sensibilidad tarifaria frente a variaciones macroeconómicas (IPC) y operativas (CDF, CBL).

## 3. Segmentos y Propuesta de Valor (Business Model Canvas)
| Segmento | Propuesta de Valor | Entregable en ClearGov |
| :--- | :--- | :--- |
| **B2B (Operadores de Aseo)** | Prevención de sanciones SSPD, validación pre-SUI y simulación de escenarios antes de aplicar tarifas. | Módulos *Auditoría CRA 1040* y *Simulador Tarifario*. |
| **B2G (Alcaldías / Entes de Control)** | Fiscalización en tiempo real de factores de subsidio/contribución y aprovechamiento de residuos. | Descarga de datasets auditados (Capa Gold) e indicadores de gestión. |
| **Ciudadanía / Veedurías** | Transparencia radical en lenguaje claro sobre el costo real del servicio por estrato. | *Visor de Datos Abiertos* y explicador de factura individual. |

## 4. Criterios de Éxito
* **Técnico:** 100% de detección de registros con valores nulos/negativos en capa Silver y 0% de error aritmético frente a las ecuaciones CRA 1040 en capa Gold.
* **Funcional:** Tiempo de procesamiento end-to-end (ingesta CSV a visualización) inferior a 3 segundos en entorno cloud.
