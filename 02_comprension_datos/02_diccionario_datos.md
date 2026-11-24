# Fase 2: Comprensión de los Datos (Data Understanding)

## 1. Fuente de Datos
Los datos provienen de los reportes operativos y comerciales mensuales consolidados por las empresas prestadoras para el **Sistema Único de Información (SUI)**, estructurados en formato tabular (`CSV`, codificación `UTF-8`). Para validación funcional se diseñó un generador sintético (`src/generate_dataset.py`) con **192 registros** correspondientes a 2 operadores, 12 periodos mensuales (`2025-01` a `2025-12`) y 8 categorías tarifarias (Estratos 1 a 6, Comercial y Oficial).

## 2. Diccionario de Variables (Esquema Capa Bronze)

| Variable | Tipo | Unidad | Dominio / Regla de Negocio | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `id_empresa` | `string` | NIT | No nulo | Identificador tributario del prestador. |
| `nombre_empresa` | `string` | Texto | No nulo | Razón social de la empresa E.S.P. |
| `municipio` | `string` | Texto | Catálogo DANE | Municipio donde se presta el servicio. |
| `departamento` | `string` | Texto | Catálogo DANE | Departamento jurisdiccional. |
| `periodo_mes` | `string` | `AAAA-MM` | Formato fecha | Mes de facturación y operación reportado. |
| `estrato` | `string` | Categoría | Estrato 1-6, Comercial, Oficial | Segmento socioeconómico o tipo de uso. |
| `suscriptores_totales` | `int` | Usuarios | $> 0$ | Número de suscriptores facturados en el mes. |
| `toneladas_no_aprovechables` | `float` | Ton/mes | $\ge 0$ | Residuos sólidos dispuestos en relleno sanitario. |
| `toneladas_aprovechadas` | `float` | Ton/mes | $\ge 0$ | Residuos efectivamente recuperados/reciclados. |
| `km_barrido_limpieza` | `float` | km/mes | $\ge 0$ | Kilómetros de vías y áreas públicas barridas. |
| `costo_comercializacion_ccs` | `float` | COP/susc | $> 0$ | Costo de Comercialización por Suscriptor. |
| `costo_barrido_cbl` | `float` | COP/susc | $\ge 0$ | Costo de Barrido y Limpieza de vías. |
| `costo_recoleccion_transporte_crt` | `float` | COP/susc | $> 0$ | Costo de Recolección y Transporte. |
| `costo_disposicion_final_cdf` | `float` | COP/susc | $> 0$ | Costo de Disposición Final en relleno. |
| `factor_subsidio_contribucion` | `float` | Proporción | $[-0.70, +1.00]$ | Factor legal Ley 142 (negativo = subsidio, positivo = aporte). |
| `tarifa_cobrada_actual` | `float` | COP/susc | $> 0$ | Tarifa final efectivamente facturada al usuario. |

## 3. Hallazgos Iniciales de Calidad de Datos
Durante la exploración inicial se identificaron tres tipologías de anomalías críticas que impactan la conformidad regulatoria:
1. **Completitud:** Registros con valores nulos (`NaN`) en `toneladas_no_aprovechables`, lo cual bloquea el cargue exitoso en el SUI.
2. **Validez de Dominio:** Valores negativos en `km_barrido_limpieza`, físicamente imposibles y causales de glosa regulatoria.
3. **Consistencia Tarifaria:** Desviaciones superiores al $+25\%$ en `tarifa_cobrada_actual` respecto al costo técnico regulado (riesgo directo de devolución de cobros y multa SSPD).
