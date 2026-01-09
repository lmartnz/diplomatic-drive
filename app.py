import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diplomatic Drive", page_icon="🚗")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    # ttl=0 asegura que no guarde caché vieja
    try:
        return conn.read(worksheet="Hoja 1", ttl=0)
    except:
        return pd.DataFrame()

def guardar_viaje(datos):
    try:
        df_actual = cargar_datos()
        # Convertimos el diccionario a DataFrame
        nuevo_df = pd.DataFrame([datos])
        # Unimos los datos nuevos con los viejos
        df_actualizado = pd.concat([df_actual, nuevo_df], ignore_index=True)
        # Enviamos a Google
        conn.update(worksheet="Hoja 1", data=df_actualizado)
        return True
    except Exception as e:
        st.error(f"Error guardando en la nube: {e}")
        return False

# --- FUNCIÓN PARA LA HORA EXACTA (Washington DC) ---
def obtener_hora_actual():
    zona_dc = pytz.timezone('America/New_York')
    # Devolvemos solo la hora (HH:MM)
    return datetime.now(zona_dc).strftime("%H:%M")

# --- CALLBACKS PARA LOS BOTONES (Evitan que se trabe) ---
def set_hora_salida():
    st.session_state.hora_salida = obtener_hora_actual()

def set_hora_llegada():
    st.session_state.hora_llegada = obtener_hora_actual()

# --- INTERFAZ GRÁFICA ---
st.title("🚗 Diplomatic Drive - Oficial")
st.markdown("*Sistema de Control de Flota - Misión OEA*")

# Menú lateral para descargar (opcional, pero útil)
with st.sidebar:
    st.header("Opciones")
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
    st.info("Conectado a Google Database Segura 🔒")

# --- FORMULARIO DE REGISTRO ---
with st.form("entry_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha del Viaje", datetime.now())
        
        st.write("---")
        # Botón y Campo de Salida
        col_btn_sal, col_input_sal = st.columns([1, 2])
        with col_btn_sal:
            st.form_submit_button("🕒 Hora Salida", on_click=set_hora_salida, type="secondary")
        with col_input_sal:
            # Si la variable no existe en memoria, la inicializamos vacía
            if 'hora_salida' not in st.session_state:
                st.session_state.hora_salida = ""
            hora_sal = st.text_input("Salida (HH:MM)", key='hora_salida')
            
        lugar_sal = st.text_input("📍 Lugar Salida")
        odo_ini = st.number_input("🔢 Odómetro Inicial", min_value=0)

    with col2:
        st.write("") 
        st.write("---")
        
        # Botón y Campo de Llegada
        col_btn_lle, col_input_lle = st.columns([1, 2])
        with col_btn_lle:
            st.form_submit_button("🏁 Hora Llegada", on_click=set_hora_llegada, type="secondary")
        with col_input_lle:
            if 'hora_llegada' not in st.session_state:
                st.session_state.hora_llegada = ""
            hora_lle = st.text_input("Llegada (HH:MM)", key='hora_llegada')

        lugar_lle = st.text_input("📍 Lugar Llegada")
        odo_fin = st.number_input("🔢 Odómetro Final", min_value=0)

    st.write("---")
    asunto = st.text_area("📝 Asunto / Misión (Detalle completo)")
    costo = st.number_input("💵 Gastos (Peajes/Parking)", min_value=0.0, format="%.2f")

    # BOTÓN FINAL DE GUARDADO
    submitted = st.form_submit_button("💾 GUARDAR VIAJE EN LA NUBE", type="primary")
    
    if submitted:
        # Validaciones
        if not asunto:
            st.error("⚠️ El asunto es obligatorio.")
        elif odo_fin < odo_ini and odo_fin != 0:
            st.error("⚠️ Error: El odómetro final es menor al inicial.")
        elif not hora_sal or not hora_lle:
             st.error("⚠️ Faltan las horas de registro.")
        else:
            # Empaquetamos los datos
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
            
            # Guardamos
            with st.spinner("Guardando en base de datos blindada..."):
                exito = guardar_viaje(nuevo_registro)
            
            if exito:
                st.success("✅ ¡Viaje registrado exitosamente!")
                # Opcional: Limpiar campos manuales si quisieras
                st.balloons()
            else:
                st.error("❌ Error de conexión con Google Sheets. Revisa los Secrets.")
