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
    "juan": {
        "name": "Juan Pérez",
        "password": "juan456"
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
    df = pd.DataFrame(datos[1:], columns=datos[0])
except Exception as e:
    st.error(f"❌ Error al cargar datos de Google Sheets: {e}")
    df = pd.DataFrame(columns=["ID", "Fecha", "Título", "Descripción", "Prioridad", "Estado", "Responsable"])

st.title("🎟️ Sistema de Tickets")

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

st.header("✏️ Editar estado de tickets")

if not filtro.empty:
    for i, row in filtro.iterrows():
        st.markdown(f"**🎫 Ticket #{row['ID']} - {row['Título']}**")

        nuevo_estado = st.selectbox(
            f"Estado actual: {row['Estado']}",
            ["Pendiente", "En curso", "Finalizado"],
            index=["Pendiente", "En curso", "Finalizado"].index(row["Estado"]),
            key=f"estado_{i}"
        )

        if st.button(f"💾 Guardar cambios en ticket #{row['ID']}", key=f"guardar_{i}"):
            try:
                # Obtener fila original en la hoja por ID
                todas_filas = sheet.get_all_records()
                for j, fila in enumerate(todas_filas, start=2):  # empieza en la fila 2
                    if fila["ID"] == row["ID"]:
                        sheet.update_cell(j, 6, nuevo_estado)  # columna 6 es 'Estado'
                        st.success(f"✅ Estado del ticket #{row['ID']} actualizado a '{nuevo_estado}'")
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error actualizando Google Sheets: {e}")
else:
    st.info("No hay tickets para mostrar o editar con los filtros actuales.")

