import streamlit as st
import pandas as pd
import datetime
import os

# === LOGIN MANUAL SIMPLE ===
USUARIOS = {
    "admin": "admin78",
    "juan": "juan456"
}

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Login")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and password == USUARIOS[usuario]:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.success("✅ Login exitoso.")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# === APP PRINCIPAL ===
st.sidebar.success(f"Bienvenido {st.session_state.usuario}")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.autenticado = False
    st.rerun()

# Archivo CSV donde se guardan los tickets
ARCHIVO = "tickets.csv"

# Cargar o crear el archivo
if os.path.exists(ARCHIVO):
    df = pd.read_csv(ARCHIVO)
else:
    df = pd.DataFrame(columns=["ID", "Fecha", "Título", "Descripción", "Prioridad", "Estado", "Responsable"])
    df.to_csv(ARCHIVO, index=False)

st.title("🎟️ Sistema de Tickets o Reclamos")

st.subheader("📋 Tickets existentes")
st.dataframe(df, use_container_width=True)

st.subheader("➕ Crear nuevo ticket")
with st.form("form_ticket"):
    titulo = st.text_input("Título")
    descripcion = st.text_area("Descripción")
    prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
    estado = "Pendiente"
    responsable = st.text_input("Responsable asignado")
    enviar = st.form_submit_button("Guardar ticket")

    if enviar:
        nueva_fila = {
            "ID": len(df) + 1,
            "Fecha": datetime.date.today().strftime("%Y-%m-%d"),
            "Título": titulo,
            "Descripción": descripcion,
            "Prioridad": prioridad,
            "Estado": estado,
            "Responsable": responsable
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        df.to_csv(ARCHIVO, index=False)
        st.success("✅ Ticket guardado correctamente")
        st.rerun()

st.subheader("🔎 Filtros")
col1, col2, col3 = st.columns(3)
with col1:
    filtro_estado = st.selectbox("Estado", ["Todos"] + df["Estado"].unique().tolist())
with col2:
    filtro_prioridad = st.selectbox("Prioridad", ["Todos"] + df["Prioridad"].unique().tolist())
with col3:
    filtro_responsable = st.selectbox("Responsable", ["Todos"] + df["Responsable"].dropna().unique().tolist())

filtro = df.copy()
if filtro_estado != "Todos":
    filtro = filtro[filtro["Estado"] == filtro_estado]
if filtro_prioridad != "Todos":
    filtro = filtro[filtro["Prioridad"] == filtro_prioridad]
if filtro_responsable != "Todos":
    filtro = filtro[filtro["Responsable"] == filtro_responsable]

st.dataframe(filtro, use_container_width=True)

st.subheader("🛠️ Actualizar estado de un ticket")
if len(df) == 0:
    st.info("No hay tickets para actualizar.")
else:
    ticket_ids = df["ID"].astype(str).tolist()
    ticket_seleccionado = st.selectbox("Seleccionar ID del ticket", ticket_ids)

    if ticket_seleccionado:
        fila = df[df["ID"] == int(ticket_seleccionado)].iloc[0]
        st.write(f"**Título:** {fila['Título']}")
        st.write(f"**Estado actual:** {fila['Estado']}")

        nuevo_estado = st.selectbox("Nuevo estado", ["Pendiente", "En curso", "Resuelto"], index=["Pendiente", "En curso", "Resuelto"].index(fila["Estado"]))
        actualizar = st.button("Actualizar estado")

        if actualizar:
            df.loc[df["ID"] == int(ticket_seleccionado), "Estado"] = nuevo_estado
            df.to_csv(ARCHIVO, index=False)
            st.success(f"Estado del ticket #{ticket_seleccionado} actualizado a '{nuevo_estado}' ✅")
            st.rerun()
