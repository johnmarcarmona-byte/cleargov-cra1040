@'
# Fase 4: Modelado Matemático y Regulatorio (Capa Gold)

## 1. Modelo Determinístico de Costo de Referencia (Resolución CRA 1040)
El **Costo de Referencia ($CR$)** por suscriptor al mes se modela mediante la agregación lineal de los cuatro componentes operativos regulados:

$$CR_{i,t} = CCS_{i,t} + CBL_{i,t} + CRT_{i,t} + CDF_{i,t}$$

Donde para el estrato $i$ en el periodo $t$:
* $CCS_{i,t}$: Costo de Comercialización por Suscriptor.
* $CBL_{i,t}$: Costo de Barrido y Limpieza de vías y áreas públicas.
* $CRT_{i,t}$: Costo de Recolección y Transporte de residuos no aprovechables.
* $CDF_{i,t}$: Costo de Disposición Final en relleno sanitario.

## 2. Modelo de Tarifa Final con Esquema Solidario (Ley 142 de 1994)
Sobre el costo técnico $CR_{i,t}$ se aplica el factor de subsidio o contribución solidaria ($f_i$) aprobado por el Concejo Municipal:

$$T^{\text{reg}}_{i,t} = CR_{i,t} \cdot (1 + f_i)$$

* Si $f_i < 0$ (Estratos 1, 2 y 3): El usuario recibe un subsidio financiado por el Fondo de Solidaridad y Redistribución de Ingresos (FSRI).
* Si $f_i = 0$ (Estrato 4 y Oficial): El usuario paga exactamente el costo técnico pleno.
* Si $f_i > 0$ (Estratos 5, 6 y Comercial): El usuario realiza un aporte solidario.

## 3. Modelo de Detección de Anomalías y Clasificación de Riesgo Tarifario
Para auditar la tarifa efectivamente facturada ($T^{\text{cob}}_{i,t}$), se calcula la desviación porcentual relativa ($D_{i,t}$):

$$D_{i,t} = \left( \frac{T^{\text{cob}}_{i,t} - T^{\text{reg}}_{i,t}}{T^{\text{reg}}_{i,t}} \right) \times 100$$

El clasificador basado en reglas asigna el estado de cumplimiento $C_{i,t}$:

```math
C_{i,t} = \begin{cases}
\text{ALTO RIESGO (Sobrecobro mayor a 3\%)} & \text{si } D_{i,t} > 3.0 \\
\text{RIESGO FINANCIERO (Subcobro mayor a 3\%)} & \text{si } D_{i,t} < -3.0 \\
\text{CUMPLIMIENTO ÓPTIMO} & \text{si } -3.0 \le D_{i,t} \le 3.0
\end{cases}