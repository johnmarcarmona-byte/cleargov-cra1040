import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

from src.etl_bronze import procesar_bronze, COLUMNAS_REQUERIDAS
from src.etl_silver import procesar_silver
from src.etl_gold import procesar_gold

# Configuración de página
st.set_page_config(
    page_title="ClearGov | Inteligencia Tarifaria CRA 1040",
    page_icon="🌿",
    layout="wide"
)

# Encabezado principal
st.title("🌿 ClearGov — Plataforma de Cumplimiento y Transparencia Tarifaria (CRA 1040)")
st.markdown(
    "Transforma datos operativos de empresas de aseo en **auditorías regulatorias**, "
    "**simulaciones tarifarias** y **visores de datos abiertos** bajo arquitectura Medallion."
)

# Barra lateral: Carga de datos (Ingesta Bronze)
st.sidebar.header("📂 1. Ingesta de Datos (Capa Bronze)")
st.sidebar.markdown("Sube el reporte CSV de la empresa de aseo o usa el dataset de demostración.")

archivo_subido = st.sidebar.file_uploader("Cargar archivo CSV de operador", type=["csv"])

# Botón para descargar plantilla CSV vacía o de ejemplo
if os.path.exists("data/01_bronze/reporte_operador_ejemplo.csv"):
    with open("data/01_bronze/reporte_operador_ejemplo.csv", "rb") as f:
        st.sidebar.download_button(
            label="📥 Descargar CSV de ejemplo",
            data=f,
            file_name="plantilla_operador_cra1040.csv",
            mime="text/csv"
        )

# Ejecución del Pipeline Medallion en tiempo real
try:
    if archivo_subido is not None:
        ruta_temp = "data/01_bronze/upload_usuario.csv"
        os.makedirs("data/01_bronze", exist_ok=True)
        with open(ruta_temp, "wb") as f:
            f.write(archivo_subido.getbuffer())
        df_bronze = procesar_bronze(ruta_temp, archivo_subido.name)
        st.sidebar.success(f"Archivo '{archivo_subido.name}' procesado.")
    else:
        df_bronze = procesar_bronze("data/01_bronze/reporte_operador_ejemplo.csv", "reporte_operador_ejemplo.csv")
        st.sidebar.info("Mostrando datos de demostración.")

    df_silver = procesar_silver(df_bronze)
    df_gold = procesar_gold(df_silver)

except Exception as e:
    st.error(f"❌ Error en el procesamiento del archivo CSV: {e}")
    st.info(f"Asegúrate de que el CSV contenga las columnas requeridas: {', '.join(COLUMNAS_REQUERIDAS)}")
    st.stop()

# Filtro global por empresa y municipio
st.sidebar.header("🏢 2. Filtros de Consulta")
empresas_disponibles = df_gold["nombre_empresa"].unique().tolist()
empresa_sel = st.sidebar.selectbox("Seleccionar Empresa Prestadora:", empresas_disponibles)

df_filtrado = df_gold[df_gold["nombre_empresa"] == empresa_sel].copy()
municipio_actual = df_filtrado["municipio"].iloc[0]
departamento_actual = df_filtrado["departamento"].iloc[0]

st.subheader(f"Operador: {empresa_sel} | 📍 {municipio_actual}, {departamento_actual}")

# Pestañas según segmentos del Business Model Canvas (B2B y B2G)
tab1, tab2, tab3, tab4 = st.tabs([
    "🛡️ Auditoría CRA 1040 (Operador B2B)",
    "🎛️ Simulador Tarifario",
    "🌐 Visor de Datos Abiertos (B2G / Ciudadanía)",
    "🏗️ Arquitectura Medallion (ETL)"
])

# ==============================================================================
# PESTAÑA 1: AUDITORÍA Y PREVENCIÓN DE SANCIONES (B2B)
# ==============================================================================
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    total_reg = len(df_filtrado)
    alertas_calidad = int(df_filtrado["tiene_alerta_calidad"].sum())
    riesgo_tarifario = len(df_filtrado[df_filtrado["estado_cumplimiento_tarifario"] != "CUMPLIMIENTO ÓPTIMO"])
    tarifa_prom = df_filtrado["tarifa_cobrada_actual"].mean()

    col1.metric("Registros Auditados", total_reg)
    col2.metric("Alertas Calidad SUI (Silver)", alertas_calidad, delta="-Revisar" if alertas_calidad > 0 else "Óptimo", delta_color="inverse")
    col3.metric("Alertas Riesgo Tarifario", riesgo_tarifario, delta="Riesgo Sanción" if riesgo_tarifario > 0 else "Sin riesgo", delta_color="inverse")
    col4.metric("Tarifa Promedio Cobrada", f"${tarifa_prom:,.0f} COP")

    st.markdown("---")
    c1, c2 = st.columns([1.3, 1])

    with c1:
        st.markdown("#### Comparación: Tarifa Cobrada vs. Tarifa Regulatoria CRA 1040 (Último Mes)")
        ultimo_mes = df_filtrado["periodo_mes"].max()
        df_mes = df_filtrado[df_filtrado["periodo_mes"] == ultimo_mes]

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=df_mes["estrato"], y=df_mes["tarifa_regulatoria_calculada"],
            name="Tarifa Regulatoria CRA 1040", marker_color="#2E86C1"
        ))
        fig_comp.add_trace(go.Bar(
            x=df_mes["estrato"], y=df_mes["tarifa_cobrada_actual"],
            name="Tarifa Cobrada por Empresa", marker_color="#28B463"
        ))
        fig_comp.update_layout(barmode="group", xaxis_title="Estrato / Uso", yaxis_title="Tarifa ($ COP)", height=380)
        st.plotly_chart(fig_comp, use_container_width=True)

    with c2:
        st.markdown("#### Semáforo de Cumplimiento Normativo")
        conteo_estado = df_filtrado["estado_cumplimiento_tarifario"].value_counts().reset_index()
        conteo_estado.columns = ["Estado", "Cantidad"]
        fig_pie = px.pie(
            conteo_estado, names="Estado", values="Cantidad", hole=0.45,
            color="Estado",
            color_discrete_map={
                "CUMPLIMIENTO ÓPTIMO": "#28B463",
                "ALTO RIESGO (Sobrecobro > 3%)": "#E74C3C",
                "RIESGO FINANCIERO (Subcobro > 3%)": "#F39C12"
            }
        )
        fig_pie.update_layout(height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("#### 🚨 Detalle de Anomalías y Alertas Detectadas (Prevención de Sanciones SSPD)")
    df_alertas = df_filtrado[
        (df_filtrado["tiene_alerta_calidad"]) |
        (df_filtrado["estado_cumplimiento_tarifario"] != "CUMPLIMIENTO ÓPTIMO")
    ][["periodo_mes", "estrato", "tarifa_regulatoria_calculada", "tarifa_cobrada_actual", "desviacion_porcentual", "estado_cumplimiento_tarifario", "auditoria_calidad_sui"]]

    if len(df_alertas) > 0:
        st.dataframe(df_alertas, use_container_width=True)
    else:
        st.success("✅ No se detectaron anomalías regulatorias ni sobrecobros para esta empresa.")

# ==============================================================================
# PESTAÑA 2: SIMULADOR TARIFARIO INTERACTIVO
# ==============================================================================
with tab2:
    st.markdown("### 🎛️ Simulador de Proyección Tarifaria antes de Aplicación")
    st.markdown("Ajusta las variables operativas y macroeconómicas para proyectar el impacto en la tarifa final por estrato.")

    sc1, sc2, sc3 = st.columns(3)
    var_ipc = sc1.slider("Proyección Incremento IPC / Costos (%)", -5.0, 20.0, 5.5, 0.5)
    var_disposicion = sc2.slider("Variación Costo Disposición Final - CDF (%)", -10.0, 30.0, 0.0, 1.0)
    var_barrido = sc3.slider("Variación Costo Barrido y Limpieza - CBL (%)", -10.0, 30.0, 0.0, 1.0)

    df_sim = df_filtrado[df_filtrado["periodo_mes"] == df_filtrado["periodo_mes"].max()].copy()
    df_sim["nuevo_ccs"] = df_sim["costo_comercializacion_ccs"] * (1 + var_ipc / 100)
    df_sim["nuevo_crt"] = df_sim["costo_recoleccion_transporte_crt"] * (1 + var_ipc / 100)
    df_sim["nuevo_cdf"] = df_sim["costo_disposicion_final_cdf"] * (1 + (var_ipc + var_disposicion) / 100)
    df_sim["nuevo_cbl"] = df_sim["costo_barrido_cbl"] * (1 + (var_ipc + var_barrido) / 100)

    df_sim["costo_ref_proyectado"] = df_sim["nuevo_ccs"] + df_sim["nuevo_crt"] + df_sim["nuevo_cdf"] + df_sim["nuevo_cbl"]
    df_sim["tarifa_proyectada"] = (df_sim["costo_ref_proyectado"] * (1 + df_sim["factor_subsidio_contribucion"])).round(2)
    df_sim["variacion_pesos"] = (df_sim["tarifa_proyectada"] - df_sim["tarifa_regulatoria_calculada"]).round(2)

    fig_sim = go.Figure()
    fig_sim.add_trace(go.Bar(x=df_sim["estrato"], y=df_sim["tarifa_regulatoria_calculada"], name="Tarifa Base Actual", marker_color="#85929E"))
    fig_sim.add_trace(go.Bar(x=df_sim["estrato"], y=df_sim["tarifa_proyectada"], name="Tarifa Simulada Proyectada", marker_color="#8E44AD"))
    fig_sim.update_layout(barmode="group", title="Impacto de la Simulación por Estrato ($ COP)", height=380)
    st.plotly_chart(fig_sim, use_container_width=True)

    st.dataframe(
        df_sim[["estrato", "factor_subsidio_contribucion", "tarifa_regulatoria_calculada", "tarifa_proyectada", "variacion_pesos"]],
        use_container_width=True
    )

# ==============================================================================
# PESTAÑA 3: VISOR DE DATOS ABIERTOS (B2G Y VEEDURÍAS CIUDADANAS)
# ==============================================================================
with tab3:
    st.markdown("### 🌐 Portal de Transparencia y Datos Abiertos para Ciudadanos y Entes de Control")
    st.markdown("Traducimos los reportes técnicos de la **Resolución CRA 1040** en información clara sobre el servicio de aseo en tu municipio.")

    # --- NUEVO BLOQUE: EXPLICADOR DE FACTURA PARA EL CIUDADANO ---
    st.markdown("#### 🧾 ¿Qué estás pagando en tu factura de aseo? (Consulta por Estrato)")
    df_ultimo_ciudadano = df_filtrado[df_filtrado["periodo_mes"] == df_filtrado["periodo_mes"].max()]
    
    estrato_ciudadano = st.selectbox(
        "Selecciona tu estrato o tipo de inmueble:",
        df_ultimo_ciudadano["estrato"].tolist(),
        key="selector_ciudadano"
    )
    fila_est = df_ultimo_ciudadano[df_ultimo_ciudadano["estrato"] == estrato_ciudadano].iloc[0]

    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Costo Pleno del Servicio", f"${fila_est['costo_referencia_cra1040']:,.0f} COP", help="Lo que cuesta prestar el servicio antes de subsidios o aportes.")
    
    factor = fila_est["factor_subsidio_contribucion"]
    etiqueta_factor = f"Subsidio recibido ({abs(factor)*100:.0f}%)" if factor < 0 else (f"Aporte solidario (+{factor*100:.0f}%)" if factor > 0 else "Sin subsidio ni aporte (0%)")
    diferencia_sub = fila_est["tarifa_cobrada_actual"] - fila_est["costo_referencia_cra1040"]
    
    fc2.metric("Ajuste Solidario (Ley 142)", f"${diferencia_sub:,.0f} COP", delta=etiqueta_factor, delta_color="normal" if factor <= 0 else "off")
    fc3.metric("Total Cobrado en tu Factura", f"${fila_est['tarifa_cobrada_actual']:,.0f} COP")

    st.info(
        f"💡 **En palabras simples:** Prestar el servicio de aseo para **{estrato_ciudadano}** en **{municipio_actual}** "
        f"tiene un costo técnico de **${fila_est['costo_referencia_cra1040']:,.0f}**. "
        f"Aplicando el esquema de solidaridad (**{etiqueta_factor}**), tu tarifa mensual es de **${fila_est['tarifa_cobrada_actual']:,.0f} COP**."
    )
    st.markdown("---")
    # --- FIN BLOQUE CIUDADANO ---

    vc1, vc2, vc3 = st.columns(3)
    suscriptores_ultimo = int(df_ultimo_ciudadano["suscriptores_totales"].sum())
    ton_totales = df_filtrado["toneladas_no_aprovechables"].sum() + df_filtrado["toneladas_aprovechadas"].sum()
    aprovechamiento_prom = df_filtrado["tasa_aprovechamiento_pct"].mean()

    vc1.metric("Suscriptores Atendidos", f"{suscriptores_ultimo:,}")
    vc2.metric("Toneladas Gestionadas (Año)", f"{ton_totales:,.1f} Ton")
    vc3.metric("Tasa Promedio Aprovechamiento", f"{aprovechamiento_prom:.1f}%")

    g1, g2 = st.columns(2)
    with g1:
        df_tendencia = df_filtrado.groupby("periodo_mes")[["toneladas_no_aprovechables", "toneladas_aprovechadas"]].sum().reset_index()
        df_tendencia.columns = ["Mes", "Basura a Relleno (Ton)", "Material Reciclado (Ton)"]
        fig_ton = px.area(
            df_tendencia, x="Mes", y=["Basura a Relleno (Ton)", "Material Reciclado (Ton)"],
            title="¿Cuánta basura generamos y cuánto reciclamos?",
            labels={"value": "Toneladas", "variable": "Destino"}
        )
        st.plotly_chart(fig_ton, use_container_width=True)

    with g2:
        nombres_amigables = {
            "costo_comercializacion_ccs": "Facturación y Atención (CCS)",
            "costo_barrido_cbl": "Barrido de Calles (CBL)",
            "costo_recoleccion_transporte_crt": "Recolección y Transporte (CRT)",
            "costo_disposicion_final_cdf": "Relleno Sanitario (CDF)"
        }
        df_costos = df_ultimo_ciudadano[list(nombres_amigables.keys())].mean().reset_index()
        df_costos.columns = ["Actividad", "Costo Promedio ($ COP)"]
        df_costos["Actividad"] = df_costos["Actividad"].map(nombres_amigables)
        
        fig_comp_cost = px.pie(
            df_costos, names="Actividad", values="Costo Promedio ($ COP)", hole=0.4,
            title="¿En qué se invierte cada peso de tu tarifa?"
        )
        st.plotly_chart(fig_comp_cost, use_container_width=True)

    csv_gold = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar Dataset Abierto Procesado (Capa Gold - CSV)",
        data=csv_gold,
        file_name=f"datos_abiertos_{municipio_actual.lower()}.csv",
        mime="text/csv"
    )
# ==============================================================================
# PESTAÑA 4: TRAZABILIDAD ARQUITECTURA MEDALLION
# ==============================================================================
with tab4:
    st.markdown("### 🏗️ Auditoría del Pipeline ETL (Arquitectura Medallion)")
    st.info("Visualización de las tres capas de transformación de datos implementadas bajo el marco CRISP-DM.")

    m1, m2, m3 = st.tabs(["🥉 Capa Bronze (Crudo)", "🥈 Capa Silver (Limpio y Auditado)", "🥇 Capa Gold (Analítico)"])
    with m1:
        st.write("Datos originales ingeridos con metadatos de trazabilidad:")
        st.dataframe(df_bronze.head(15), use_container_width=True)
    with m2:
        st.write("Datos estandarizados con reglas de validación SUI y tratamiento de valores nulos/negativos:")
        st.dataframe(df_silver.head(15), use_container_width=True)
    with m3:
        st.write("Tabla analítica final con cálculo de tarifas CRA 1040, desviaciones y KPIs:")
        st.dataframe(df_gold.head(15), use_container_width=True)