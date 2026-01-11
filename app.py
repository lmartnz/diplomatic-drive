import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from streamlit_gsheets import GSheetsConnection
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diplomatic Drive", page_icon="🚗", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos():
    try:
        # Leemos la hoja principal de bitácora
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

# --- FUNCIÓN DE HORA (Washington DC) ---
def obtener_hora_actual():
    zona_dc = pytz.timezone('America/New_York')
    return datetime.now(zona_dc).strftime("%H:%M")

def obtener_timestamp_dc():
    zona_dc = pytz.timezone('America/New_York')
    return str(datetime.now(zona_dc))

# --- CALLBACKS (Solución para botones) ---
def set_hora_salida():
    st.session_state.hora_salida = obtener_hora_actual()

def set_hora_llegada():
    st.session_state.hora_llegada = obtener_hora_actual()

# ==========================================
# 🔽 MENÚ LATERAL 🔽
# ==========================================

with st.sidebar:
    # Bandera oficial
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Costa_Rica.svg/320px-Flag_of_Costa_Rica.svg.png", width=100)
    st.title("Diplomatic Drive")
    st.subheader("Misión Permanente OEA")
    
    menu = st.radio(
        "Menú Principal",
        ["🏠 Inicio", "📅 Agenda", "🚗 Bitácora Oficial", "📄 Reportes Cancillería", "⚙️ Mantenimiento"],
        index=0
    )
    
    st.markdown("---")
    st.caption("🟢 Sistema En Línea | V 1.2")

# ==========================================
# 🔽 LÓGICA DE PÁGINAS 🔽
# ==========================================

# 1. INICIO
if menu == "🏠 Inicio":
    st.title("Bienvenido, Luis")
    st.markdown("### 🛡️ Panel de Control Oficial")
    st.info("Sistema listo para operar. Seleccione 'Bitácora Oficial' para registrar movimientos.")

# 2. AGENDA
elif menu == "📅 Agenda":
    st.title("📅 Agenda de Movimientos")
    st.write("🚧 Módulo de Integración con Outlook (Fase 2)")

# 3. BITÁCORA (Con Memoria y Sin Error Rojo)
elif menu == "🚗 Bitácora Oficial":
    st.title("📒 Registro de Movimientos")
    st.markdown("*Formulario conectado a Base de Datos Segura*")
    
    # --- MEMORIA INTELIGENTE ---
    df = cargar_datos()
    def_lugar_salida = ""
    def_odo_inicial = 0
    
    if not df.empty:
        ultimo_viaje = df.iloc[-1]
        def_lugar_salida = ultimo_viaje.get("lugar_llegada", "")
        def_odo_inicial = int(ultimo_viaje.get("odo_final", 0))
    
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
            
            lugar_sal = st.text_input("📍 Lugar Salida", value=def_lugar_salida)
            odo_ini = st.number_input("🔢 Odómetro Inicial", min_value=0, value=def_odo_inicial)

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
        asunto = st.text_area("📝 Asunto / Misión (Detalle para reporte)")
        costo = st.number_input("💵 Gastos ($)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("💾 GUARDAR EN NUBE", type="primary")
        
        if submitted:
            # Validaciones
            if not asunto:
                st.error("⚠️ Falta el Asunto.")
            elif odo_fin < odo_ini and odo_fin != 0:
                 st.error(f"⚠️ Error: El odómetro final no puede ser menor al inicial.")
            else:
                # Datos con Timestamp corregido (DC)
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
                    "timestamp_registro": obtener_timestamp_dc() # <--- CORREGIDO AQUI
                }
                
                with st.spinner("Encriptando y guardando..."):
                    if guardar_viaje(nuevo_registro):
                        st.success("✅ ¡Viaje registrado exitosamente!")
                        st.balloons()
                        # NOTA: Quitamos las líneas que borraban el estado para evitar el error rojo.
                        # Al hacer rerun, se actualiza la memoria inteligente.
                        st.rerun()

# 4. REPORTES (Privado y con Excel)
elif menu == "📄 Reportes Cancillería":
    st.title("🖨️ Centro de Reportes")
    st.markdown("### Generación de Informes Oficiales")
    st.info("🔒 Área segura: Los datos no se muestran en pantalla por privacidad.")
    
    st.write("---")
    
    # Filtros de Fecha
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        inicio = st.date_input("Desde:", value=datetime.now().date().replace(day=1))
    with col_f2:
        fin = st.date_input("Hasta:", value=datetime.now().date())
        
    st.write("")
    
    # Botón de Generación
    if st.button("📊 PROCESAR DATOS DEL PERIODO"):
        df = cargar_datos()
        
        if not df.empty:
            # Convertir fecha para filtrar
            df["fecha_dt"] = pd.to_datetime(df["fecha"]).dt.date
            mask = (df["fecha_dt"] >= inicio) & (df["fecha_dt"] <= fin)
            df_filtrado = df.loc[mask]
            
            if not df_filtrado.empty:
                # Preparamos el Excel en memoria
                buffer = io.BytesIO()
                
                # Seleccionamos solo columnas oficiales (sin timestamp)
                columnas_oficiales = [
                    "fecha", "hora_salida", "lugar_salida", "odo_inicial", 
                    "hora_llegada", "lugar_llegada", "odo_final", "costo", "asunto"
                ]
                
                # Creamos el Excel usando Pandas (motor openpyxl)
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_filtrado[columnas_oficiales].to_excel(writer, index=False, sheet_name='Bitacora_Oficial')
                    
                valioso_excel = buffer.getvalue()
                
                st.success(f"✅ Se encontraron {len(df_filtrado)} registros listos.")
                
                # Botón de Descarga
                nombre_archivo = f"Reporte_Oficial_{inicio}_{fin}.xlsx"
                st.download_button(
                    label="⬇️ DESCARGAR EXCEL OFICIAL",
                    data=valioso_excel,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            else:
                st.warning("⚠️ No hay viajes registrados en esas fechas.")
        else:
            st.error("No hay conexión con la base de datos.")

# 5. MANTENIMIENTO
elif menu == "⚙️ Mantenimiento":
    st.title("⚙️ Taller y Mantenimiento")
    st.write("Próximamente: Control de Aceite y Llantas.")
