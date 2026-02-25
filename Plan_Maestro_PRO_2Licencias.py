import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# ============================================
# SISTEMA DE LICENCIAS CON LÍMITE DE 2 ACTIVACIONES
# ============================================

LICENCIAS = {
    "PRO-001": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-002": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-003": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-004": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-005": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-006": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-007": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-008": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-009": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
    "PRO-010": {"expira": "2026-12-31", "activa": True, "max_usos": 2},
}

ARCHIVO_USOS = "usos_plan_maestro.json"

def cargar_usos():
    if os.path.exists(ARCHIVO_USOS):
        with open(ARCHIVO_USOS, "r") as f:
            return json.load(f)
    return {}

def guardar_usos(usos):
    with open(ARCHIVO_USOS, "w") as f:
        json.dump(usos, f, indent=2)

def verificar_licencia():
    if st.session_state.get("licencia_validada", False):
        return True
    
    usos_registrados = cargar_usos()
    
    st.sidebar.header("🔐 Acceso PRO")
    codigo = st.sidebar.text_input("Código de licencia", type="password", key="codigo_licencia")
    
    if st.sidebar.button("Activar licencia"):
        if codigo in LICENCIAS:
            if not LICENCIAS[codigo]["activa"]:
                st.sidebar.error("❌ Licencia desactivada")
                return False
            
            fecha_exp = datetime.strptime(LICENCIAS[codigo]["expira"], "%Y-%m-%d")
            if datetime.now() > fecha_exp:
                st.sidebar.error("❌ Licencia expirada")
                return False
            
            usos_actuales = usos_registrados.get(codigo, 0)
            max_usos = LICENCIAS[codigo]["max_usos"]
            
            if usos_actuales >= max_usos:
                st.sidebar.error(f"❌ Límite de {max_usos} alcanzado")
                return False
            
            usos_registrados[codigo] = usos_actuales + 1
            guardar_usos(usos_registrados)
            
            st.session_state.licencia_validada = True
            st.session_state.codigo_usado = codigo
            st.sidebar.success(f"✅ Activada ({usos_actuales + 1}/{max_usos})")
            st.rerun()
        else:
            st.sidebar.error("❌ Código inválido")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("💳 [Comprar licencia](https://wa.me/5218715791810)")
    st.warning("🔒 Versión PRO bloqueada")
    return False

# Configuración
st.set_page_config(page_title="Plan Maestro 2028-2049", layout="wide")

if not verificar_licencia():
    st.stop()

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("📊 PLAN MAESTRO DE VIDA 2028–2049")
st.markdown("**22 Años - Etapa de Acumulación**")
st.caption("Basado en el modelo financiero de Roberto Villarreal")
st.divider()

# ============================================
# FUNCIÓN DE CÁLCULO
# ============================================

def calcular_plan(
    capital_inicial=360000,
    tasa_interes=0.10,
    ahorro_imss_inicial=3500,
    incremento_anual=0.05,
    aguinaldo_inicial=16500,
    pension_bienestar_inicial=4750,
    retiros_especiales=None
):
    años = list(range(2028, 2050))
    data = []

    capital = capital_inicial
    ahorro_imss = ahorro_imss_inicial
    pension_bienestar = 0
    aguinaldo = aguinaldo_inicial

    for i, año in enumerate(años):
        retiro = retiros_especiales.get(año, 0) if retiros_especiales else 0
        interes = capital * tasa_interes

        if año == 2029:
            interes -= 3500
        elif año == 2030:
            interes -= 2500

        if año < 2038:
            pct_flujo = 0.80
            pct_reinversion = 0.20
        else:
            pct_flujo = 0.20
            pct_reinversion = 0.80

        if año < 2038:
            aguinaldo_prorrateado = aguinaldo / 12
            aguinaldo_reinvertido = 0
            aguinaldo_mostrar = 0
        else:
            aguinaldo_prorrateado = 0
            aguinaldo_reinvertido = aguinaldo
            aguinaldo_mostrar = aguinaldo

        capital_final = capital + (interes * pct_reinversion) - retiro + aguinaldo_reinvertido
        flujo_mensual = (interes * pct_flujo) / 12

        if año > 2028:
            ahorro_imss = ahorro_imss * (1 + incremento_anual)

        if año >= 2034:
            if año == 2034:
                pension_bienestar = pension_bienestar_inicial
            else:
                pension_bienestar = pension_bienestar * (1 + incremento_anual)
            pension_bienestar_mensual = pension_bienestar / 2
        else:
            pension_bienestar_mensual = 0

        total_mensual = flujo_mensual + ahorro_imss + pension_bienestar_mensual + aguinaldo_prorrateado

        data.append({
            "Año": año,
            "Capital Inicial": capital,
            "Retiro Especial": retiro,
            "Interés Ganado": round(interes, 2),
            "Aguinaldo": aguinaldo_mostrar,
            "Capital Final": round(capital_final, 2),
            "Flujo Mensual": round(flujo_mensual, 2),
            "Ahorro IMSS": round(ahorro_imss, 2),
            "Pensión Bienestar (bim)": round(pension_bienestar, 2) if pension_bienestar > 0 else 0,
            "Total Mensual": round(total_mensual, 2)
        })

        aguinaldo = aguinaldo * (1 + incremento_anual)
        capital = capital_final

    return pd.DataFrame(data)

# ============================================
# SIDEBAR
# ============================================

st.sidebar.header("⚙️ Parámetros del Plan")

capital_inicial = st.sidebar.number_input("Capital inicial ($)", value=360000, step=10000)
tasa_interes = st.sidebar.slider("Tasa de interés anual (%)", 5.0, 15.0, 10.0) / 100
ahorro_imss_inicial = st.sidebar.number_input("Ahorro IMSS inicial ($/mes)", value=3500, step=100)
incremento_anual = st.sidebar.slider("Incremento anual (%)", 3.0, 7.0, 5.0) / 100
aguinaldo_inicial = st.sidebar.number_input("Aguinaldo inicial 2028 ($)", value=16500, step=500)
pension_bienestar_inicial = st.sidebar.number_input("Pensión Bienestar inicial 2034 ($/bim)", value=4750, step=100)

st.sidebar.divider()
st.sidebar.markdown("### 📌 Retiros Especiales (5)")

retiro1_activo = st.sidebar.checkbox("Activar Retiro 1", value=True, key="r1")
if retiro1_activo:
    año_retiro1 = st.sidebar.selectbox("Año del Retiro 1", list(range(2028, 2050)), index=1, key="a1")
    monto_retiro1 = st.sidebar.number_input("Monto Retiro 1 ($)", value=190000, step=10000, key="m1")
else:
    año_retiro1 = None
    monto_retiro1 = 0

retiro2_activo = st.sidebar.checkbox("Activar Retiro 2", value=True, key="r2")
if retiro2_activo:
    año_retiro2 = st.sidebar.selectbox("Año del Retiro 2", list(range(2028, 2050)), index=6, key="a2")
    monto_retiro2 = st.sidebar.number_input("Monto Retiro 2 ($)", value=50000, step=5000, key="m2")
else:
    año_retiro2 = None
    monto_retiro2 = 0

retiro3_activo = st.sidebar.checkbox("Activar Retiro 3", value=False, key="r3")
if retiro3_activo:
    año_retiro3 = st.sidebar.selectbox("Año del Retiro 3", list(range(2028, 2050)), index=10, key="a3")
    monto_retiro3 = st.sidebar.number_input("Monto Retiro 3 ($)", value=30000, step=5000, key="m3")
else:
    año_retiro3 = None
    monto_retiro3 = 0

retiro4_activo = st.sidebar.checkbox("Activar Retiro 4", value=False, key="r4")
if retiro4_activo:
    año_retiro4 = st.sidebar.selectbox("Año del Retiro 4", list(range(2028, 2050)), index=12, key="a4")
    monto_retiro4 = st.sidebar.number_input("Monto Retiro 4 ($)", value=25000, step=5000, key="m4")
else:
    año_retiro4 = None
    monto_retiro4 = 0

retiro5_activo = st.sidebar.checkbox("Activar Retiro 5", value=False, key="r5")
if retiro5_activo:
    año_retiro5 = st.sidebar.selectbox("Año del Retiro 5", list(range(2028, 2050)), index=15, key="a5")
    monto_retiro5 = st.sidebar.number_input("Monto Retiro 5 ($)", value=20000, step=5000, key="m5")
else:
    año_retiro5 = None
    monto_retiro5 = 0

retiros_por_año = {}
if retiro1_activo and año_retiro1:
    retiros_por_año[año_retiro1] = monto_retiro1
if retiro2_activo and año_retiro2:
    retiros_por_año[año_retiro2] = monto_retiro2
if retiro3_activo and año_retiro3:
    retiros_por_año[año_retiro3] = monto_retiro3
if retiro4_activo and año_retiro4:
    retiros_por_año[año_retiro4] = monto_retiro4
if retiro5_activo and año_retiro5:
    retiros_por_año[año_retiro5] = monto_retiro5

# ============================================
# CÁLCULO
# ============================================

if st.button("🚀 Calcular Plan", type="primary", use_container_width=True):
    df = calcular_plan(
        capital_inicial=capital_inicial,
        tasa_interes=tasa_interes,
        ahorro_imss_inicial=ahorro_imss_inicial,
        incremento_anual=incremento_anual,
        aguinaldo_inicial=aguinaldo_inicial,
        pension_bienestar_inicial=pension_bienestar_inicial,
        retiros_especiales=retiros_por_año
    )

    st.subheader("📋 Proyección 2028–2049")

    df_display = df.copy()
    for col in ["Capital Inicial", "Retiro Especial", "Interés Ganado", "Aguinaldo",
                "Capital Final", "Flujo Mensual", "Ahorro IMSS", "Pensión Bienestar (bim)", "Total Mensual"]:
        df_display[col] = df_display[col].apply(lambda x: f"${x:,.0f}" if x != 0 else "$0")

    st.dataframe(df_display, use_container_width=True, hide_index=True)
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Evolución del Capital")
        fig_capital = px.line(df, x="Año", y="Capital Final", markers=True)
        fig_capital.update_traces(line_color="#0066b3", line_width=3)
        fig_capital.update_layout(yaxis_title="Capital ($)", yaxis_tickformat="$,.0f")
        st.plotly_chart(fig_capital, use_container_width=True)

    with col2:
        st.subheader("📈 Total Mensual Disponible")
        fig_mensual = px.line(df, x="Año", y="Total Mensual", markers=True)
        fig_mensual.update_traces(line_color="#00a86b", line_width=3)
        fig_mensual.update_layout(yaxis_title="Ingreso mensual ($)", yaxis_tickformat="$,.0f")
        st.plotly_chart(fig_mensual, use_container_width=True)

    st.divider()

    st.subheader("📊 Composición del Ingreso Mensual")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Flujo Intereses", x=df["Año"], y=df["Flujo Mensual"]))
    fig.add_trace(go.Bar(name="Ahorro IMSS", x=df["Año"], y=df["Ahorro IMSS"]))
    fig.add_trace(go.Bar(name="Pensión Bienestar (mensual)", x=df["Año"], y=df["Pensión Bienestar (bim)"]/2))
    fig.update_layout(barmode='stack', xaxis_title="Año", yaxis_title="Ingreso mensual ($)",
                      yaxis_tickformat="$,.0f", height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("🎯 Resumen al 2049")
    ultimo = df.iloc[-1]

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        st.metric("Capital Final", f"${ultimo['Capital Final']:,.0f}")
    with col_r2:
        st.metric("Total Mensual", f"${ultimo['Total Mensual']:,.0f}")
    with col_r3:
        st.metric("Ahorro IMSS", f"${ultimo['Ahorro IMSS']:,.0f}")
    with col_r4:
        st.metric("Pensión Bienestar (bim)", f"${ultimo['Pensión Bienestar (bim)']:,.0f}")

    st.success(f"✅ **Capital final en 2049:** ${ultimo['Capital Final']:,.0f}")

st.divider()
st.caption("© Ing. Roberto Villarreal - Plan Maestro con licencia")