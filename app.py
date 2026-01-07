import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta  # <--- AGREGAMOS TIMEDELTA AQUÍ
from io import BytesIO
from openpyxl import load_workbook

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="DiplomaticDrive", page_icon="🇨🇷", layout="wide")

# --- CONEXIÓN A BASE DE DATOS ---
def get_connection():
    return sqlite3.connect('mision.db')

# --- MENÚ LATERAL ---
st.title("🇨🇷 DiplomaticDrive")
st.sidebar.header("Menú Oficial")
opcion = st.sidebar.radio("Ir a:", ["Inicio", "Agenda", "Bitácora Oficial", "Reportes Cancillería"])

# --- 1. SECCIÓN INICIO ---
if opcion == "Inicio":
    st.markdown("### 👋 Panel de Control - Misión Permanente")
    
    conn = get_connection()
    try:
        total_viajes = conn.execute("SELECT COUNT(*) FROM bitacora").fetchone()[0]
    except:
        total_viajes = 0
    conn.close()
    
    st.info("Sistema listo para el registro oficial de la flota diplomática.")
    st.metric("Viajes Totales Registrados", total_viajes)

# --- 2. SECCIÓN AGENDA ---
elif opcion == "Agenda":
    st.header("📅 Agenda Oficial")
    conn = get_connection()
    try:
        df_agenda = pd.read_sql_query("SELECT titulo, fecha_hora, ubicacion FROM agenda", conn)
        st.dataframe(df_agenda, use_container_width=True)
    except:
        st.warning("No hay datos de agenda aún.")
    conn.close()

# --- 3. SECCIÓN BITÁCORA OFICIAL ---
elif opcion == "Bitácora Oficial":
    st.header("⛽ Registro de Movimiento (Formulario 074-CB-DGSE)")
    st.markdown("Complete los datos exactos conforme al reglamento.")
    
    with st.form("form_oficial"):
        # Fecha del movimiento
        col_fecha, col_vacio = st.columns([1, 2])
        fecha = col_fecha.date_input("Fecha del viaje", value=datetime.now())
        
        st.markdown("---")
        
        # BLOQUE 1: SALIDA
        st.subheader("🚩 SALIDA")
        c1, c2, c3 = st.columns(3)
        # AQUI AGREGAMOS step=60 PARA MINUTOS EXACTOS
        hora_sal = c1.time_input("Hora Salida", key="h_sal", step=60) 
        lugar_sal = c2.text_input("Lugar Salida", value="Misión/Residencia")
        odo_ini = c3.number_input("Odómetro Inicial", min_value=0, step=1)
        
        # BLOQUE 2: DESTINO
        st.subheader("🏁 DESTINO (LLEGADA)")
        c4, c5, c6 = st.columns(3)
        # AQUI AGREGAMOS step=60 PARA MINUTOS EXACTOS
        hora_lle = c4.time_input("Hora Llegada", key="h_lle", step=60)
        lugar_lle = c5.text_input("Lugar Llegada")
        odo_fin = c6.number_input("Odómetro Final", min_value=0, step=1)
        
        st.markdown("---")
        
        # BLOQUE 3: DETALLES
        c7, c8 = st.columns([3, 1])
        asunto = c7.text_input("Motivo / Justificación (Oficial)")
        costo = c8.number_input("Costo ($)", min_value=0.0, step=1.0, help="Peajes, parqueo, etc.")
        
        # BOTÓN DE GUARDADO
        submitted = st.form_submit_button("💾 REGISTRAR MOVIMIENTO OFICIAL")
        
        if submitted:
            # Validaciones
            if odo_fin < odo_ini:
                st.error("❌ ERROR: El kilometraje final no puede ser menor al inicial.")
            elif not asunto:
                st.error("❌ ERROR: Debe indicar el motivo del viaje.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO bitacora (fecha, hora_salida, lugar_salida, odo_inicial, 
                                          hora_llegada, lugar_llegada, odo_final, costo, asunto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (fecha, str(hora_sal), lugar_sal, odo_ini, str(hora_lle), lugar_lle, odo_fin, costo, asunto))
                conn.commit()
                conn.close()
                
                distancia = odo_fin - odo_ini
                st.success(f"✅ REGISTRO EXITOSO: Se recorrieron {distancia} km.")

# --- 4. SECCIÓN REPORTES (PLANTILLA OFICIAL) ---
elif opcion == "Reportes Cancillería":
    st.header("📂 Exportación Oficial (Formato Ministerio)")
    st.markdown("Genera el Excel idéntico al oficial sobre la plantilla.")

    # --- NUEVO: FILTRO DE FECHAS ---
    st.markdown("### 📅 Seleccione la Semana a Reportar")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        # Por defecto muestra desde hace 7 días
        f_inicio = st.date_input("Desde:", value=datetime.now() - timedelta(days=7))
    with col_f2:
        # Hasta hoy
        f_fin = st.date_input("Hasta:", value=datetime.now())

    st.write(f"Generando reporte desde **{f_inicio}** hasta **{f_fin}**")
    # -------------------------------
    
    if st.button("🔄 Generar Reporte Excel Oficial"):
        conn = get_connection()
        cursor = conn.cursor()
        
        # --- NUEVO: CONSULTA SQL CON FILTRO ---
        # Solo traemos los viajes que estén ENTRE las fechas seleccionadas
        query = "SELECT * FROM bitacora WHERE date(fecha) >= date(?) AND date(fecha) <= date(?)"
        cursor.execute(query, (f_inicio, f_fin))
        # --------------------------------------
        
        datos = cursor.fetchall()
        conn.close()
        
        if not datos:
            st.warning(f"⚠️ No hay viajes registrados entre el {f_inicio} y el {f_fin}.")
        else:
            try:
                # Cargar la plantilla que debes tener en la carpeta
                wb = load_workbook("plantilla_oficial.xlsx")
                ws = wb.active 
                
                # --- CONFIGURACIÓN DE COLUMNAS ---
                # Ajusta estos números según tu Excel oficial
                FILA_INICIAL = 16 
                
                for i, viaje in enumerate(datos):
                    fila = FILA_INICIAL + i
                    # viaje = (id, fecha, h_sal, lug_sal, odo_ini, h_lle, lug_lle, odo_fin, costo, asunto)
                    
                    # FECHA (Columna A = 1)
                    ws.cell(row=fila, column=1, value=viaje[1])
                    
                    # SALIDA: Odometro (Col B=2), Lugar (Col C=3), Hora (Col D=4)
                    ws.cell(row=fila, column=2, value=viaje[4]) # Odo Ini
                    ws.cell(row=fila, column=3, value=viaje[3]) # Lugar Sal
                    ws.cell(row=fila, column=4, value=viaje[2]) # Hora Sal
                    
                    # --- BLOQUE LLEGADA (Corregido) ---
                    
                    # Columna E (5) -> Km Final (Odómetro Final)
                    ws.cell(row=fila, column=5, value=viaje[7]) 
                    
                    # Columna F (6) -> Lugar Llegada (Asumiendo que está en el medio, letra F)
                    ws.cell(row=fila, column=6, value=viaje[6]) 
                    
                    # Columna G (7) -> Hora Llegada
                    ws.cell(row=fila, column=7, value=viaje[5])
                    
                    # CALCULOS: Km Recorridos (Col H=8)
                    km_recorridos = viaje[7] - viaje[4]
                    ws.cell(row=fila, column=8, value=km_recorridos)
                    
                    # COSTO (Col J=10) - Saltamos la I (Totales)
                    ws.cell(row=fila, column=10, value=viaje[8])
                    
                    # JUSTIFICACION (Col K=11)
                    ws.cell(row=fila, column=11, value=viaje[9])

                # Guardar en memoria para descargar
                buffer = BytesIO()
                wb.save(buffer)
                buffer.seek(0)
                
                st.success(f"✅ Reporte generado: {len(datos)} viajes encontrados en ese rango.")
                st.download_button(
                    label="📥 Descargar Excel Listo (.xlsx)",
                    data=buffer,
                    file_name=f"Bitacora_{f_inicio}_al_{f_fin}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except FileNotFoundError:
                st.error("❌ ERROR: No encuentro el archivo 'plantilla_oficial.xlsx' en la carpeta.")
                st.info("Asegúrate de guardar el Excel vacío con ese nombre exacto.")
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")