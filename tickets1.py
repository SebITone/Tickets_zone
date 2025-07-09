import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# ------------------------
# Login manual sin Hasher
# ------------------------
usuarios = {
    "admin": {
        "name": "admin",
        "password": "admin78"
    },
    "sebs": {
        "name": "Sebastián",
        "password": "sebs76"
    }
}


# Inicializar el estado de sesión si no existe
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# ------------------------
# Mostrar login solo si no está autenticado
# ------------------------
if not st.session_state["logged_in"]:
    st.title("Gestor de Tickets y Reclamos")

    st.subheader("Centralizá, organizá y hacé seguimiento de todos los incidentes desde un solo lugar")

    st.text("Esta aplicación permite registrar, clasificar y hacer seguimiento de reclamos o solicitudes de manera ágil y transparente. Cada ticket queda asociado a un cliente, área o responsable, facilitando la priorización y resolución eficiente. Ideal para equipos de soporte, atención al cliente o gestión interna que buscan trazabilidad y orden en su flujo de trabajo.")

    
    st.title("🎟️ Sistema de Tickets - Login")

    username_input = st.text_input("Usuario")
    password_input = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if username_input in usuarios and usuarios[username_input]["password"] == password_input:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username_input
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# ------------------------
# App principal
# ------------------------
st.sidebar.success(f"Bienvenido {usuarios[st.session_state['username']]['name']}")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

# Acceso a Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=SCOPE)
client = gspread.authorize(CREDS)

SHEET_NAME = "streamlit_tickets"
WORKSHEET_NAME = "Hoja 1"

try:
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    datos = sheet.get_all_records()
    df = pd.DataFrame(datos)
except Exception as e:
    st.error(f"❌ Error al cargar datos de Google Sheets: {e}")
    df = pd.DataFrame(columns=["ID", "Fecha", "Título", "Descripción", "Prioridad", "Estado", "Responsable"])

st.title("🎟️ Gestor de Tickets y Reclamos")

st.header("📋 Tickets existentes")
st.dataframe(df, use_container_width=True)

st.header("➕ Crear nuevo ticket")
with st.form("form_ticket"):
    titulo = st.text_input("Título")
    descripcion = st.text_area("Descripción")
    prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
    estado = "Pendiente"
    responsable = st.text_input("Responsable asignado")
    enviar = st.form_submit_button("Guardar ticket")

    if enviar:
        nueva_fila = [len(df) + 1, datetime.date.today().strftime("%Y-%m-%d"),
                      titulo, descripcion, prioridad, estado, responsable]
        sheet.append_row(nueva_fila)
        st.success("✅ Ticket guardado correctamente")
        st.rerun()

st.header("🔎 Filtros")
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

st.header("✏️ Editar ticket (estado y descripción)")

if not filtro.empty:
    ids_disponibles = filtro["ID"].tolist()
    id_seleccionado = st.selectbox("Seleccioná el ticket a editar (por ID)", ids_disponibles)

    # Obtener la fila del ticket seleccionado
    ticket = filtro[filtro["ID"] == id_seleccionado].iloc[0]

    nuevo_estado = st.selectbox(
        f"Estado actual: {ticket['Estado']}",
        ["Pendiente", "En curso", "Finalizado"],
        index=["Pendiente", "En curso", "Finalizado"].index(ticket["Estado"])
    )

    nueva_descripcion = st.text_area("Editar descripción", value=ticket["Descripción"])

    if st.button("💾 Guardar cambios"):
        try:
            # Buscar la fila real por ID en el archivo completo
            todas_filas = sheet.get_all_records()
            for j, fila in enumerate(todas_filas, start=2):  # desde la fila 2 por encabezado
                if fila["ID"] == ticket["ID"]:
                    sheet.update_cell(j, 4, nueva_descripcion)  # columna 4 = "Descripción"
                    sheet.update_cell(j, 6, nuevo_estado)       # columna 6 = "Estado"
                    st.success(f"✅ Ticket #{ticket['ID']} actualizado correctamente")
                    st.rerun()
        except Exception as e:
            st.error(f"❌ Error actualizando el ticket: {e}")
else:
    st.info("No hay tickets para editar con los filtros actuales.")



