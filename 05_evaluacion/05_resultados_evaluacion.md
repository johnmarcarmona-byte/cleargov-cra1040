# Fase 5: Evaluación de Modelos y Calidad (Evaluation)

## 1. Metodología de Validación
Para verificar la eficacia de los modelos de auditoría y cálculo tarifario antes del despliegue productivo, se aplicó una **prueba controlada de inyección de fallos** sobre los 192 registros operativos, introduciendo tres anomalías críticas representativas de errores reales en prestadores:
1. **Registro #5:** Sobrecobro tarifario intencional del $+25\%$ sobre la tarifa regulada.
2. **Registro #12:** Valor nulo (`NaN`) en `toneladas_no_aprovechables`.
3. **Registro #20:** Valor negativo (`-15.0 km`) en `km_barrido_limpieza`.

## 2. Matriz de Resultados de Evaluación

| Componente Evaluado | Métrica | Resultado Obtenido | Umbral Aceptación | Estado |
| :--- | :--- | :---: | :---: | :---: |
| **Auditoría Calidad SUI (Silver)** | Sensibilidad (Recall) | **100% (2/2)** | $\ge 95\%$ | Aprobado |
| **Imputación Estratificada (Silver)** | Nulos / Negativos residuales | **0 registros** | $0$ | Aprobado |
| **Motor Ecuaciones CRA 1040 (Gold)** | Error Absoluto Máximo (MAE) | **$0.000000$ COP** | $< 0.01$ COP | Aprobado |
| **Clasificador Riesgo Tarifario (Gold)** | Precisión y Recall en sobrecobros | **100% (1/1)** | $100\%$ | Aprobado |
| **Rendimiento Pipeline End-to-End** | Latencia total (Bronze $\rightarrow$ Gold) | **$< 0.18$ seg** | $< 2.00$ seg | Aprobado |

## 3. Verificación Automatizada
El script `05_evaluacion/validar_modelos.py` ejecuta las aserciones matemáticas y lógicas sobre el pipeline completo, garantizando que cualquier actualización futura del código mantenga la integridad regulatoria.
