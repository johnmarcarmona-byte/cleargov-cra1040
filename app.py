import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import time

from src.etl_bronze import procesar_bronze, COLUMNAS_REQUERIDAS
from src.etl_silver import procesar_silver
from src.etl_gold import procesar_gold

st.set_page_config(
    page_title="ClearGov | Inteligencia Tarifaria CRA 1040",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 ClearGov — Plataforma de Cumplimiento y Transparencia Tarifaria (CRA 1040)")
st.markdown(
    "Transforma datos operativos de empresas de aseo en **visores de datos abiertos**, "
    "**auditorías regulatorias** y **simulaciones tarifarias** bajo arquitectura Medallion."
)

if "datos_procesados" not in st.session_state:
    st.session_state["datos_procesados"] = False
    st.session_state["nombre_archivo_activo"] = "reporte_operador_ejemplo.csv"
    st.session_state["ruta_activa"] = "data/01_bronze/reporte_operador_ejemplo.csv"

st.sidebar.header("📂 1. Ingesta de Datos (Capa Bronze)")
st.sidebar.markdown("Sube el reporte CSV de la empresa de aseo y presiona **Procesar Datos**.")

archivo_subido = st.sidebar.file_uploader("Cargar archivo CSV de operador", type=["csv"])

if archivo_subido is not None:
    if st.sidebar.button("🚀 Procesar Datos (Ejecutar ETL)", type="primary", use_container_width=True):
        ruta_temp = "data/01_bronze/upload_usuario.csv"
        os.makedirs("data/01_bronze", exist_ok=True)
        with open(ruta_temp, "wb") as f:
            f.write(archivo_subido.getbuffer())
        
        barra = st.sidebar.progress(0, text="Iniciando ingesta Capa Bronze...")
        time.sleep(0.35)
        barra.progress(35, text="🥉 Capa Bronze: Validando esquema CRA 1040...")
        time.sleep(0.35)
        barra.progress(70, text="🥈 Capa Silver: Auditando calidad SUI...")
        time.sleep(0.35)
        barra.progress(100, text="🥇 Capa Gold: Calculando tarifas y KPIs...")
        time.sleep(0.25)
        barra.empty()

        st.session_state["ruta_activa"] = ruta_temp
        st.session_state["nombre_archivo_activo"] = archivo_subido.name
        st.session_state["datos_procesados"] = True

    if st.session_state["datos_procesados"] and st.session_state["nombre_archivo_activo"] == archivo_subido.name:
        st.sidebar.success(f"✅ Prueba ejecutada con: '{archivo_subido.name}'")
    else:
        st.sidebar.warning("⏳ Archivo cargado. Haz clic en 'Procesar Datos' para ejecutar el ETL.")
else:
    st.session_state["ruta_activa"] = "data/01_bronze/reporte_operador_ejemplo.csv"
    st.session_state["nombre_archivo_activo"] = "reporte_operador_ejemplo.csv"
    st.session_state["datos_procesados"] = False
    st.sidebar.info("ℹ️ Mostrando dataset de demostración precargado.")

if os.path.exists("data/01_bronze/reporte_operador_ejemplo.csv"):
    with open("data/01_bronze/reporte_operador_ejemplo.csv", "rb") as f:
        st.sidebar.download_button(
            label="📥 Descargar CSV de ejemplo",
            data=f,
            file_name="plantilla_operador_cra1040.csv",
            mime="text/csv",
            use_container_width=True
        )

try:
    df_bronze = procesar_bronze(st.session_state["ruta_activa"], st.session_state["nombre_archivo_activo"])
    df_silver = procesar_silver(df_bronze)
    df_gold = procesar_gold(df_silver)
except Exception as e:
    st.error(f"❌ Error en el procesamiento del archivo CSV: {e}")
    st.info(f"Asegúrate de que el CSV contenga las columnas requeridas: {', '.join(COLUMNAS_REQUERIDAS)}")
    st.stop()

st.sidebar.header("🏢 2. Filtros de Consulta")
empresas_disponibles = df_gold["nombre_empresa"].unique().tolist()
empresa_sel = st.sidebar.selectbox("Seleccionar Empresa Prestadora:", empresas_disponibles)

df_filtrado = df_gold[df_gold["nombre_empresa"] == empresa_sel].copy()
municipio_actual = df_filtrado["municipio"].iloc[0]
departamento_actual = df_filtrado["departamento"].iloc[0]

st.subheader(f"Operador: {empresa_sel} | 📍 {municipio_actual}, {departamento_actual}")

tab_ciudadano, tab_auditoria, tab_simulador, tab_medallion = st.tabs([
    "🌐 Visor de Datos Abiertos (B2G / Ciudadanía)",
    "🛡️ Auditoría CRA 1040 (Operador B2B)",
    "🎛️ Simulador Tarifario",
    "🏗️ Arquitectura Medallion (ETL)"
])

with tab_ciudadano:
    st.markdown("### 🌐 Portal de Transparencia y Datos Abiertos para Ciudadanos y Entes de Control")
    st.markdown("Traducimos los reportes técnicos de la **Resolución CRA 1040** en información clara sobre el servicio de aseo en tu municipio.")

    st.markdown("#### 🧾 ¿Qué estás pagando en tu factura de aseo? (Consulta por Estrato)")
    df_ultimo_ciudadano = df_filtrado[df_filtrado["periodo_mes"] == df_filtrado["periodo_mes"].max()]
    
    estrato_ciudadano = st.selectbox(
        "Selecciona tu estrato o tipo de inmueble:",
        df_ultimo_ciudadano["estrato"].tolist(),
        key="selector_ciudadano"
    )
    fila_est = df_ultimo_ciudadano[df_ultimo_ciudadano["estrato"] == estrato_ciudadano].iloc[0]

    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Costo Pleno del Servicio (CR)", f"${fila_est['costo_referencia_cra1040']:,.0f} COP", help="Suma de CCS + CBL + CRT + CDF + CLUS antes de subsidios o aportes.")
    
    factor = fila_est["factor_subsidio_contribucion"]
    etiqueta_factor = f"Subsidio recibido ({abs(factor)*100:.0f}%)" if factor < 0 else (f"Aporte solidario (+{factor*100:.0f}%)" if factor > 0 else "Sin subsidio ni aporte (0%)")
    diferencia_sub = fila_est["tarifa_cobrada_actual"] - fila_est["costo_referencia_cra1040"]
    
    fc2.metric("Ajuste Solidario (Ley 142)", f"${diferencia_sub:,.0f} COP", delta=etiqueta_factor, delta_color="normal" if factor <= 0 else "off")
    fc3.metric("Total Cobrado en tu Factura", f"${fila_est['tarifa_cobrada_actual']:,.0f} COP")

    st.info(
        f"💡 **En palabras simples:** Prestar el servicio de aseo para **{estrato_ciudadano}** en **{municipio_actual}** "
        f"tiene un costo técnico pleno de **${fila_est['costo_referencia_cra1040']:,.0f}** (incluyendo limpieza urbana CLUS). "
        f"Aplicando el esquema de solidaridad (**{etiqueta_factor}**), tu tarifa mensual es de **${fila_est['tarifa_cobrada_actual']:,.0f} COP**."
    )
    st.markdown("---")

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
            "costo_disposicion_final_cdf": "Relleno Sanitario (CDF)",
            "costo_limpieza_urbana_clus": "Limpieza Urbana / Césped / Árboles (CLUS)"
        }
        df_costos = df_ultimo_ciudadano[list(nombres_amigables.keys())].mean().reset_index()
        df_costos.columns = ["Actividad", "Costo Promedio ($ COP)"]
        df_costos["Actividad"] = df_costos["Actividad"].map(nombres_amigables)
        
        fig_comp_cost = px.pie(
            df_costos, names="Actividad", values="Costo Promedio ($ COP)", hole=0.4,
            title="¿En qué se invierte cada peso de tu tarifa? (5 Componentes CRA 1040)"
        )
        st.plotly_chart(fig_comp_cost, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        csv_gold = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Dataset Abierto Procesado (Capa Gold - CSV)",
            data=csv_gold,
            file_name=f"datos_abiertos_{municipio_actual.lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d2:
        json_gold_str = df_ultimo_ciudadano[[
            "id_empresa", "nombre_empresa", "municipio", "periodo_mes", "estrato",
            "costo_comercializacion_ccs", "costo_barrido_cbl", "costo_recoleccion_transporte_crt",
            "costo_disposicion_final_cdf", "costo_limpieza_urbana_clus",
            "costo_referencia_cra1040", "factor_subsidio_contribucion", "tarifa_cobrada_actual"
        ]].to_json(orient="records", force_ascii=False, indent=2)
        st.download_button(
            label="📦 Descargar Respuesta API / Datos Abiertos (JSON)",
            data=json_gold_str.encode("utf-8"),
            file_name=f"api_tarifas_{municipio_actual.lower()}.json",
            mime="application/json",
            use_container_width=True
        )

    with st.expander("🔌 Integración Web SaaS para Empresas Clientes (Código Iframe y Payload JSON)"):
        st.markdown("Si una empresa prestadora adquiere **ClearGov SaaS**, puede incrustar este visor directamente en su portal web corporativo copiando esta etiqueta HTML o consumiendo el JSON estructurado:")
        col_emb1, col_emb2 = st.columns(2)
        with col_emb1:
            st.markdown("**1. Código HTML Embebible (`<iframe>`) para sitio web:**")
            st.code(
                '<iframe src="https://cleargov-cra1040-8jiowai5bj6mdvjrz5wv5u.streamlit.app/?embed=true"\n'
                '        width="100%" height="780" frameborder="0"></iframe>',
                language="html"
            )
        with col_emb2:
            st.markdown(f"**2. Salida JSON en tiempo real ({estrato_ciudadano}):**")
            payload_ejemplo = {
                "empresa": empresa_sel,
                "nit": str(fila_est["id_empresa"]),
                "municipio": municipio_actual,
                "marco_regulatorio": "Resolución CRA 1040",
                "periodo": str(fila_est["periodo_mes"]),
                "estrato": estrato_ciudadano,
                "componentes_cop": {
                    "CCS": float(fila_est["costo_comercializacion_ccs"]),
                    "CBL": float(fila_est["costo_barrido_cbl"]),
                    "CRT": float(fila_est["costo_recoleccion_transporte_crt"]),
                    "CDF": float(fila_est["costo_disposicion_final_cdf"]),
                    "CLUS": float(fila_est["costo_limpieza_urbana_clus"])
                },
                "costo_referencia_cop": float(fila_est["costo_referencia_cra1040"]),
                "factor_ley142": float(fila_est["factor_subsidio_contribucion"]),
                "tarifa_final_cop": float(fila_est["tarifa_cobrada_actual"])
            }
            st.json(payload_ejemplo)

with tab_auditoria:
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

with tab_simulador:
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
    df_sim["nuevo_clus"] = df_sim["costo_limpieza_urbana_clus"] * (1 + (var_ipc + var_barrido) / 100)

    df_sim["costo_ref_proyectado"] = (
        df_sim["nuevo_ccs"] + df_sim["nuevo_crt"] + df_sim["nuevo_cdf"] + df_sim["nuevo_cbl"] + df_sim["nuevo_clus"]
    )
    df_sim["tarifa_proyectada"] = (df_sim["costo_ref_proyectado"] * (1 + df_sim["factor_subsidio_contribucion"])).round(2)
    df_sim["variacion_pesos"] = (df_sim["tarifa_proyectada"] - df_sim["tarifa_regulatoria_calculada"]).round(2)
    df_sim["variacion_pct"] = ((df_sim["variacion_pesos"] / df_sim["tarifa_regulatoria_calculada"]) * 100).round(2)

    impacto_pct_prom = df_sim["variacion_pct"].mean()
    impacto_cop_prom = df_sim["variacion_pesos"].mean()
    recaudo_actual = (df_sim["tarifa_regulatoria_calculada"] * df_sim["suscriptores_totales"]).sum()
    recaudo_proy = (df_sim["tarifa_proyectada"] * df_sim["suscriptores_totales"]).sum()
    delta_recaudo = recaudo_proy - recaudo_actual

    ic1, ic2, ic3 = st.columns(3)
    ic1.metric(
        "Impacto Porcentual Promedio en Tarifa",
        f"{impacto_pct_prom:+.2f}%",
        delta=f"{impacto_pct_prom:+.2f}% vs. tarifa base",
        delta_color="inverse" if impacto_pct_prom > 0 else "normal"
    )
    ic2.metric(
        "Variación Promedio por Suscriptor",
        f"${impacto_cop_prom:+,.0f} COP / mes",
        delta=f"{impacto_pct_prom:+.2f}%",
        delta_color="inverse" if impacto_cop_prom > 0 else "normal"
    )
    ic3.metric(
        "Impacto en Recaudo Mensual Total",
        f"${recaudo_proy:,.0f} COP",
        delta=f"${delta_recaudo:+,.0f} COP ({impacto_pct_prom:+.2f}%)",
        delta_color="normal"
    )

    etiquetas_base = [f"${v:,.0f}" for v in df_sim["tarifa_regulatoria_calculada"]]
    etiquetas_proy = [
        f"${v:,.0f}<br>({p:+.1f}%)"
        for v, p in zip(df_sim["tarifa_proyectada"], df_sim["variacion_pct"])
    ]

    fig_sim = go.Figure()
    fig_sim.add_trace(go.Bar(
        x=df_sim["estrato"],
        y=df_sim["tarifa_regulatoria_calculada"],
        name="Tarifa Base Actual",
        marker_color="#85929E",
        text=etiquetas_base,
        textposition="outside"
    ))
    fig_sim.add_trace(go.Bar(
        x=df_sim["estrato"],
        y=df_sim["tarifa_proyectada"],
        name="Tarifa Simulada Proyectada",
        marker_color="#8E44AD",
        text=etiquetas_proy,
        textposition="outside"
    ))
    max_y = max(df_sim["tarifa_proyectada"].max(), df_sim["tarifa_regulatoria_calculada"].max()) * 1.22
    fig_sim.update_layout(
        barmode="group",
        title=f"Impacto de la Simulación por Estrato ($ COP y % de variación: {impacto_pct_prom:+.2f}%)",
        yaxis=dict(range=[0, max_y], title="Tarifa Mensual ($ COP)"),
        xaxis_title="Estrato / Uso",
        height=440
    )
    st.plotly_chart(fig_sim, use_container_width=True)

    st.dataframe(
        df_sim[["estrato", "factor_subsidio_contribucion", "tarifa_regulatoria_calculada", "tarifa_proyectada", "variacion_pesos", "variacion_pct"]],
        use_container_width=True
    )

with tab_medallion:
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
