import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diplomatic Drive", page_icon="🚗", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIONES DE BASE DE DATOS (Globales) ---
def cargar_datos():
    try:
        return conn.read(worksheet="Hoja 1", ttl=0)
    except:
        return pd.DataFrame()

def guardar_viaje(datos):
    try:
        df_actual = cargar_datos()
        nuevo_df = pd.DataFrame([datos])
        df_actualizado = pd.concat([df_actual, nuevo_df], ignore_index=True)
        conn.update(worksheet="Hoja 1", data=df_actualizado)
        return True
    except Exception as e:
        st.error(f"Error guardando en la nube: {e}")
        return False

# --- FUNCIÓN DE HORA ---
def obtener_hora_actual():
    zona_dc = pytz.timezone('America/New_York')
    return datetime.now(zona_dc).strftime("%H:%M")

# --- CALLBACKS PARA BOTONES ---
def set_hora_salida():
    st.session_state.hora_salida = obtener_hora_actual()

def set_hora_llegada():
    st.session_state.hora_llegada = obtener_hora_actual()

# ==========================================
# 🔽 AQUÍ EMPIEZA TU MENÚ LATERAL 🔽
# ==========================================

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Costa_Rica.svg/320px-Flag_of_Costa_Rica.svg.png", width=100)
    st.title("Diplomatic Drive")
    st.subheader("Misión Permanente OEA")
    
    # El Menú de Navegación
    menu = st.radio(
        "Navegación",
        ["🏠 Inicio", "📅 Agenda", "🚗 Bitácora Oficial", "📄 Reportes Cancillería", "⚙️ Mantenimiento"],
        index=0
    )
    
    st.markdown("---")
    st.info("🟢 Sistema: En Línea")
    st.caption("Conexión Segura: Google Cloud")

# ==========================================
# 🔽 LOGICA DE CADA PAGINA 🔽
# ==========================================

# 1. PÁGINA DE INICIO
if menu == "🏠 Inicio":
    st.title("Bienvenido, Luis")
    st.markdown("### Panel de Control - Misión Diplomática")
    
    # Mostrar un resumen rápido si hay datos
    df = cargar_datos()
    if not df.empty:
        total_viajes = len(df)
        st.metric("Total Viajes Registrados", total_viajes)
    else:
        st.info("No hay viajes registrados aún en la nueva base de datos.")

# 2. PÁGINA DE AGENDA (Placeholder)
elif menu == "📅 Agenda":
    st.title("Agenda de la Embajadora")
    st.write("🚧 Integración con Outlook en construcción (Fase 2)...")

# 3. PÁGINA DE BITÁCORA (AQUÍ ESTÁ LA MAGIA NUEVA)
elif menu == "🚗 Bitácora Oficial":
    st.title("📒 Registro de Movimientos Oficiales")
    st.markdown("*Formulario conectado a Google Sheets*")
    
    with st.form("entry_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha del Viaje", datetime.now())
            st.write("---")
            
            # Botón Salida
            col_b1, col_i1 = st.columns([1,2])
            with col_b1:
                st.form_submit_button("🕒 Salida", on_click=set_hora_salida, type="secondary")
            with col_i1:
                if 'hora_salida' not in st.session_state: st.session_state.hora_salida = ""
                hora_sal = st.text_input("Hora Salida", key='hora_salida')
                
            lugar_sal = st.text_input("📍 Lugar Salida")
            odo_ini = st.number_input("🔢 Odómetro Inicial", min_value=0)

        with col2:
            st.write("")
            st.write("---")
            
            # Botón Llegada
            col_b2, col_i2 = st.columns([1,2])
            with col_b2:
                st.form_submit_button("🏁 Llegada", on_click=set_hora_llegada, type="secondary")
            with col_i2:
                if 'hora_llegada' not in st.session_state: st.session_state.hora_llegada = ""
                hora_lle = st.text_input("Hora Llegada", key='hora_llegada')

            lugar_lle = st.text_input("📍 Lugar Llegada")
            odo_fin = st.number_input("🔢 Odómetro Final", min_value=0)

        st.write("---")
        asunto = st.text_area("📝 Asunto / Misión")
        costo = st.number_input("💵 Gastos ($)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("💾 GUARDAR EN NUBE", type="primary")
        
        if submitted:
            if not asunto:
                st.error("⚠️ Falta el Asunto.")
            else:
                nuevo_registro = {
                    "fecha": str(fecha),
                    "hora_salida": str(hora_sal),
                    "lugar_salida": lugar_sal,
                    "odo_inicial": int(odo_ini),
                    "hora_llegada": str(hora_lle),
                    "lugar_llegada": lugar_lle,
                    "odo_final": int(odo_fin),
                    "costo": float(costo),
                    "asunto": asunto,
                    "timestamp_registro": str(datetime.now())
                }
                
                with st.spinner("Guardando..."):
                    if guardar_viaje(nuevo_registro):
                        st.success("✅ ¡Guardado en Google Sheets!")
                        st.balloons()

# 4. PÁGINA DE REPORTES
elif menu == "📄 Reportes Cancillería":
    st.title("Generador de Reportes")
    st.write("Aquí podrás descargar el Excel semanal.")
    
    # Botón para descargar lo que hay en Google Sheets
    df = cargar_datos()
    if not df.empty:
        st.dataframe(df)
        # Convertir a CSV para descarga simple
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar Copia de Seguridad", csv, "bitacora_backup.csv", "text/csv")

# 5. PÁGINA DE MANTENIMIENTO
elif menu == "⚙️ Mantenimiento":
    st.title("Control de Mantenimiento")
    st.write("🚧 Próximamente: Alertas de cambio de aceite y llantas.")

