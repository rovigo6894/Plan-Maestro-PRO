import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import platform
import os
import json

# ============================================
# SISTEMA DE LICENCIAS MEJORADO (2 MÁQUINAS)
# ============================================

def get_machine_id():
    """Genera un identificador único para la máquina"""
    machine_info = f"{platform.node()}-{platform.processor()}-{os.name}"
    return hashlib.md5(machine_info.encode()).hexdigest()[:10]

# Base de datos de licencias
LICENCIAS = {
    "CLIENTE1-A3F8": {
        "expira": "2026-12-31", 
        "activa": True, 
        "max_maquinas": 2,
        "maquinas_autorizadas": []
    },
    "CLIENTE2-X7K9": {
        "expira": "2026-12-31", 
        "activa": True, 
        "max_maquinas": 2,
        "maquinas_autorizadas": []
    },
    "DEMO-CLIENTE": {
        "expira": "2026-12-31", 
        "activa": True, 
        "max_maquinas": 2,
        "maquinas_autorizadas": []
    },
}

ARCHIVO_LICENCIAS = "licencias_plan_maestro.json"

def cargar_licencias():
    """Carga el estado de las licencias desde archivo"""
    if os.path.exists(ARCHIVO_LICENCIAS):
        with open(ARCHIVO_LICENCIAS, "r") as f:
            return json.load(f)
    return {}

def guardar_licencias(estado):
    """Guarda el estado de las licencias en archivo"""
    with open(ARCHIVO_LICENCIAS, "w") as f:
        json.dump(estado, f, indent=2)

def verificar_licencia():
    """Verifica licencia por máquina"""
    
    if st.session_state.get("licencia_validada", False):
        return True
    
    machine_id = get_machine_id()
    estado_licencias = cargar_licencias()
    
    st.sidebar.header("🔐 Acceso PRO")
    codigo = st.sidebar.text_input("Código de licencia", type="password")
    
    if st.sidebar.button("Activar licencia"):
        if codigo in LICENCIAS:
            licencia = LICENCIAS[codigo]
            
            # Verificar si la licencia está activa
            if not licencia["activa"]:
                st.sidebar.error("❌ Licencia desactivada")
                return False
            
            # Verificar fecha de expiración
            fecha_exp = datetime.strptime(licencia["expira"], "%Y-%m-%d")
            if datetime.now() > fecha_exp:
                st.sidebar.error("❌ Licencia expirada")
                return False
            
            # Cargar máquinas autorizadas para este código
            maquinas = estado_licencias.get(codigo, [])
            
            # Si la máquina ya está autorizada, acceso directo
            if machine_id in maquinas:
                st.session_state.licencia_validada = True
                st.session_state.codigo_usado = codigo
                st.sidebar.success("✅ Acceso concedido")
                st.rerun()
                return True
            
            # Si es una máquina nueva, verificar límite
            if len(maquinas) < licencia["max_maquinas"]:
                # Registrar nueva máquina
                maquinas.append(machine_id)
                estado_licencias[codigo] = maquinas
                guardar_licencias(estado_licencias)
                
                st.session_state.licencia_validada = True
                st.session_state.codigo_usado = codigo
                st.sidebar.success(f"✅ Máquina registrada ({len(maquinas)}/{licencia['max_maquinas']})")
                st.rerun()
                return True
            else:
                st.sidebar.error(f"❌ Límite de {licencia['max_maquinas']} máquinas alcanzado")
                st.sidebar.info("💡 Usa el código en las máquinas ya registradas o adquiere otra licencia")
                return False
        else:
            st.sidebar.error("❌ Código inválido")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("💳 [Comprar licencia](https://wa.me/5218715791810)")
    st.warning("🔒 Versión PRO bloqueada. Ingresa un código válido en la barra lateral.")
    return False

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================

st.set_page_config(page_title="Plan Maestro PRO", layout="wide")

if not verificar_licencia():
    st.stop()

# Ocultar menús de Streamlit
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
# PARÁMETROS EDITABLES
# ============================================

st.sidebar.header("⚙️ Parámetros")

capital_inicial = st.sidebar.number_input("Capital inicial ($)", value=360000, step=10000)
tasa_interes = st.sidebar.slider("Tasa interés anual (%)", 5.0, 15.0, 10.0) / 100
ahorro_imss_inicial = st.sidebar.number_input("Ahorro IMSS inicial ($/mes)", value=3500, step=100)
incremento_anual = st.sidebar.slider("Incremento anual (%)", 3.0, 7.0, 5.0) / 100
aguinaldo_inicial = st.sidebar.number_input("Aguinaldo inicial 2028 ($)", value=16500, step=500)
pension_bienestar_inicial = st.sidebar.number_input("Pensión Bienestar 2034 ($/bim)", value=4750, step=100)

st.sidebar.divider()
st.sidebar.markdown("### 📌 Retiros (5)")

retiros_por_año = {}
for i in range(1, 6):
    activo = st.sidebar.checkbox(f"Retiro {i}", value=(i<=2), key=f"activo_{i}")
    if activo:
        año = st.sidebar.selectbox(f"Año retiro {i}", list(range(2028,2050)), 
                                   index=1 if i==1 else 6, key=f"año_{i}")
        monto = st.sidebar.number_input(f"Monto retiro {i} ($)", 
                                       value=190000 if i==1 else 50000, 
                                       step=5000, key=f"monto_{i}")
        retiros_por_año[año] = monto

# ============================================
# CÁLCULO Y VISUALIZACIÓN
# ============================================

if st.button("🚀 Calcular Plan", type="primary", use_container_width=True):
    with st.spinner("Calculando proyección..."):
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
        
        # Formato de moneda para la tabla
        df_display = df.copy()
        for col in ["Capital Inicial", "Retiro Especial", "Interés Ganado", "Aguinaldo",
                    "Capital Final", "Flujo Mensual", "Ahorro IMSS", 
                    "Pensión Bienestar (bim)", "Total Mensual"]:
            df_display[col] = df_display[col].apply(lambda x: f"${x:,.0f}" if x != 0 else "$0")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.divider()
        
        # Gráficas
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
        
        # Gráfica de composición
        st.subheader("📊 Composición del Ingreso Mensual")
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Flujo Intereses", x=df["Año"], y=df["Flujo Mensual"]))
        fig.add_trace(go.Bar(name="Ahorro IMSS", x=df["Año"], y=df["Ahorro IMSS"]))
        fig.add_trace(go.Bar(name="Pensión Bienestar (mensual)", x=df["Año"], 
                             y=df["Pensión Bienestar (bim)"]/2))
        fig.update_layout(barmode='stack', xaxis_title="Año", 
                         yaxis_title="Ingreso mensual ($)",
                         yaxis_tickformat="$,.0f", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Resumen
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

st.divider()
st.caption("© Ing. Roberto Villarreal - Plan Maestro PRO con licencia por máquina")

# ============================================
# DESCARGA DE ARCHIVOS (SOLO PARA ADMIN)
# ============================================

with st.expander("⚙️ Admin (protegido)"):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://img.icons8.com/color/48/000000/admin-settings-male.png", width=50)
    with col2:
        st.markdown("### 🔐 Área administrativa")
    
    password = st.text_input("Contraseña de administrador", type="password")
    
    CONTRASENA_ADMIN = "Villarreal2026"  # Misma contraseña
    
    if password == CONTRASENA_ADMIN:
        st.success("✅ Acceso concedido")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("**📊 Estado actual:**")
            # 👇 ESTA ES LA ÚNICA LÍNEA QUE CAMBIA (nombre del archivo)
            archivo_licencias = "licencias_plan_maestro.json"
            
            if os.path.exists(archivo_licencias):
                with open(archivo_licencias, "r") as f:
                    datos = json.load(f)
                st.info(f"📁 Licencias registradas: {len(datos)}")
                
                # Botón de descarga
                with open(archivo_licencias, "rb") as f:
                    from datetime import datetime
                    st.download_button(
                        label="📥 Descargar licencias_plan_maestro.json",
                        data=f,
                        file_name=f"licencias_plan_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.warning("⚠️ No hay archivo de licencias aún")
        
        with col_a2:
            st.markdown("**📝 Últimas activaciones:**")
            archivo_licencias = "licencias_plan_maestro.json"
            if os.path.exists(archivo_licencias):
                with open(archivo_licencias, "r") as f:
                    datos = json.load(f)
                if datos:
                    items = list(datos.items())[-5:]
                    for codigo, maquinas in items:
                        st.markdown(f"- **{codigo}**: {len(maquinas)} máquina(s)")
                else:
                    st.markdown("*Sin datos*")
            else:
                st.markdown("*Sin activaciones*")
    elif password != "":
        st.error("❌ Contraseña incorrecta")
