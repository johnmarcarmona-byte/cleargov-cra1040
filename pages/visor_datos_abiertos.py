import streamlit as st
import pandas as pd
import plotly.express as px
import os

from src.etl_bronze import procesar_bronze
from src.etl_silver import procesar_silver
from src.etl_gold import procesar_gold

st.set_page_config(
    page_title="Visor de Datos Abiertos | ClearGov",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar por completo la barra lateral, la navegación multipágina y la cabecera de Streamlit
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 1.2rem !important; }
    </style>
    """,
    unsafe_allow_html=True
)

ruta_datos = "data/01_bronze/upload_usuario.csv" if os.path.exists("data/01_bronze/upload_usuario.csv") else "data/01_bronze/reporte_operador_ejemplo.csv"
df_bronze = procesar_bronze(ruta_datos, os.path.basename(ruta_datos))
df_silver = procesar_silver(df_bronze)
df_gold = procesar_gold(df_silver)

empresas = df_gold["nombre_empresa"].unique().tolist()
empresa_sel = empresas[0]
df_filtrado = df_gold[df_gold["nombre_empresa"] == empresa_sel].copy()
municipio_actual = df_filtrado["municipio"].iloc[0]

st.markdown("### 🌐 Portal de Transparencia y Datos Abiertos para Ciudadanos y Entes de Control")
st.markdown("Traducimos los reportes técnicos de la **Resolución CRA 1040** en información clara sobre el servicio de aseo en tu municipio.")

st.markdown("#### 🧾 ¿Qué estás pagando en tu factura de aseo? (Consulta por Estrato)")
df_ultimo_ciudadano = df_filtrado[df_filtrado["periodo_mes"] == df_filtrado["periodo_mes"].max()]

estrato_ciudadano = st.selectbox(
    "Selecciona tu estrato o tipo de inmueble:",
    df_ultimo_ciudadano["estrato"].tolist(),
    key="selector_ciudadano_embed"
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
