import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="DiplomaticDrive", page_icon="🚗", layout="wide")

# --- CONEXIÓN A BASE DE DATOS ---
def get_connection():
    return sqlite3.connect('mision.db')

# --- TÍTULO Y BARRA LATERAL ---
st.title("🚗 DiplomaticDrive - Panel de Control")
st.sidebar.header("Menú Principal")
opcion = st.sidebar.radio("Ir a:", ["Inicio", "Agenda", "Bitácora (Conductor)", "Reportes"])

# --- PÁGINA: INICIO ---
if opcion == "Inicio":
    st.markdown("### 👋 Bienvenido, Luis")
    st.info("Sistema de gestión logística de la Misión Permanente activado.")
    
    # Métricas rápidas (KPIs)
    conn = get_connection()
    total_viajes = conn.execute("SELECT COUNT(*) FROM bitacora").fetchone()[0]
    total_eventos = conn.execute("SELECT COUNT(*) FROM agenda").fetchone()[0]
    conn.close()
    
    col1, col2 = st.columns(2)
    col1.metric("Viajes Registrados", total_viajes)
    col2.metric("Eventos en Agenda", total_eventos)

# --- PÁGINA: AGENDA ---
elif opcion == "Agenda":
    st.header("📅 Agenda Oficial")
    
    # Mostrar tabla de eventos
    conn = get_connection()
    df_agenda = pd.read_sql_query("SELECT titulo, fecha_hora, ubicacion, estado FROM agenda", conn)
    conn.close()
    
    if not df_agenda.empty:
        st.dataframe(df_agenda, use_container_width=True)
    else:
        st.warning("No hay eventos programados.")

# --- PÁGINA: BITÁCORA (CONDUCTOR) ---
elif opcion == "Bitácora (Conductor)":
    st.header("⛽ Registro de Kilometraje")
    st.markdown("Ingresa los datos al finalizar cada traslado.")
    
    with st.form("form_viaje"):
        col1, col2 = st.columns(2)
        odo_ini = col1.number_input("Odómetro Inicial", min_value=0, step=1)
        odo_fin = col2.number_input("Odómetro Final", min_value=0, step=1)
        asunto = st.text_input("Asunto / Motivo del viaje")
        
        submitted = st.form_submit_button("💾 Registrar Viaje")
        
        if submitted:
            if odo_fin < odo_ini:
                st.error("Error: El odómetro final no puede ser menor al inicial.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO bitacora (odo_inicial, odo_final, asunto) VALUES (?, ?, ?)", 
                            (odo_ini, odo_fin, asunto))
                conn.commit()
                conn.close()
                st.success(f"¡Viaje registrado! Distancia: {odo_fin - odo_ini} km")

# --- PÁGINA: REPORTES ---
elif opcion == "Reportes":
    st.header("📄 Informe Semanal Automatizado")
    
    if st.button("Generar Informe para Embajadora"):
        conn = get_connection()
        
        # Datos Agenda
        eventos = conn.execute("SELECT titulo, fecha_hora FROM agenda").fetchall()
        # Datos Viajes
        viajes = conn.execute("SELECT odo_inicial, odo_final, asunto FROM bitacora").fetchall()
        conn.close()
        
        # Generación del Texto
        st.markdown("---")
        st.subheader(f"Informe Semanal - {datetime.now().strftime('%Y-%m-%d')}")
        
        st.markdown("**1. Resumen de Actividades:**")
        if eventos:
            for ev in eventos:
                st.write(f"- ✅ {ev[1]}: {ev[0]}")
        else:
            st.write("(Sin eventos)")
            
        st.markdown("**2. Control de Movilidad:**")
        total_km = 0
        if viajes:
            for v in viajes:
                km = v[1] - v[0]
                total_km += km
                st.write(f"- 🚗 {v[2]} ({km} km)")
        
        st.success(f"⛽ TOTAL KILÓMETROS RECORRIDOS: {total_km} km")
        st.markdown("---")
        st.caption("Generado automáticamente por DiplomaticDrive System.")