# Asegúrate de que las dependencias estén instaladas en tu entorno:
# pip install streamlit pandas matplotlib

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Inicializar sesión si no existen las variables
if 'tickets' not in st.session_state:
    st.session_state.tickets = []

if 'ticket_id' not in st.session_state:
    st.session_state.ticket_id = 1

st.title("Gestión de Requerimientos Internos")
st.markdown("Esta app permite al Project Manager registrar y hacer seguimiento de los requerimientos para los equipos de diseño y administrativos.")

st.header("Crear nuevo requerimiento")

# Formulario para entrada de datos
with st.form("form_ticket"):
    descripcion = st.text_area("Descripción del requerimiento", height=100)
    prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
    asignado_a = st.text_input("Asignado a")
    enviado_por = st.text_input("Enviado por")
    estado = st.selectbox("Estado del requerimiento", ["Abierto", "En progreso", "Cerrado"])
    fecha_asignacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_cierre = "" if estado != "Cerrado" else fecha_asignacion
    enviar = st.form_submit_button("Agregar requerimiento")

    if enviar and descripcion and asignado_a and enviado_por:
        nuevo_ticket = {
            "ID": st.session_state.ticket_id,
            "Descripción": descripcion,
            "Prioridad": prioridad,
            "Estado": estado,
            "Fecha de asignación": fecha_asignacion,
            "Fecha de cierre": fecha_cierre,
            "Asignado a": asignado_a,
            "Enviado por": enviado_por
        }
        st.session_state.tickets.append(nuevo_ticket)
        st.session_state.ticket_id += 1
        st.success("Requerimiento agregado correctamente")

st.header("Lista de requerimientos")

# Aplicar filtros
st.sidebar.header("Filtros")
estado_filtro = st.sidebar.multiselect("Filtrar por estado", ["Abierto", "En progreso", "Cerrado"], default=["Abierto", "En progreso", "Cerrado"])
prioridad_filtro = st.sidebar.multiselect("Filtrar por prioridad", ["Alta", "Media", "Baja"], default=["Alta", "Media", "Baja"])
asignado_filtro = st.sidebar.text_input("Filtrar por asignado a").lower()

if st.session_state.tickets:
    # Procesamiento inicial del DataFrame
    df = pd.DataFrame(st.session_state.tickets)
    if 'Cerrado por' not in df.columns:
        df['Cerrado por'] = df.get('Cerrado por', '')
    df["Fecha de asignación"] = pd.to_datetime(df["Fecha de asignación"], errors='coerce')
    df["Fecha de cierre"] = pd.to_datetime(df["Fecha de cierre"], errors='coerce')
    df["✅"] = df["Estado"].apply(lambda x: "✅" if x == "Cerrado" else ("🕓" if x == "Abierto" else "🔄"))

    hoy = datetime.now()
    df["⚠️"] = df.apply(
        lambda row: "🔴 Más de 3 días abierto" if row["Estado"] == "Abierto" and (hoy - row["Fecha de asignación"]).days > 3 else "",
        axis=1
    )

    # Aplicar filtros
    df_filtrado = df[
        df["Estado"].isin(estado_filtro) &
        df["Prioridad"].isin(prioridad_filtro) &
        df["Asignado a"].str.lower().str.contains(asignado_filtro, na=False)
    ]

    st.subheader("Tabla de requerimientos")
    st.dataframe(df_filtrado, use_container_width=True)

    # Exportación("📥 Exportar a CSV", data=df_filtrado.to_csv(index=False).encode("utf-8"), file_name="requerimientos.csv", mime="text/csv")

    # Métricas
    st.header("📊 Métricas Generales")
    total_tickets = len(df)
    tickets_abiertos = len(df[df["Estado"] == "Abierto"])
    tickets_en_progreso = len(df[df["Estado"] == "En progreso"])
    tickets_cerrados = len(df[df["Estado"] == "Cerrado"])
    tiempo_cierre = df.dropna(subset=["Fecha de cierre"])

    if not tiempo_cierre.empty:
        tiempo_cierre["Duración (días)"] = (tiempo_cierre["Fecha de cierre"] - tiempo_cierre["Fecha de asignación"]).dt.days
        promedio_dias_cierre = tiempo_cierre["Duración (días)"].mean()
    else:
        promedio_dias_cierre = 0

    st.metric("Total de tickets", total_tickets)
    st.metric("Tickets abiertos", tickets_abiertos)
    st.metric("Tickets en progreso", tickets_en_progreso)
    st.metric("Tickets cerrados", tickets_cerrados)
    st.metric("Promedio días para cerrar", f"{promedio_dias_cierre:.2f} días")

    
else:
    st.info("No hay requerimientos aún.")




