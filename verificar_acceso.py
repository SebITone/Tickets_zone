import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configurar el acceso a Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)

# Conectarse al cliente de gspread
client = gspread.authorize(CREDS)

# Mostrar las hojas disponibles
st.title("🔍 Verificación de acceso a hojas de cálculo")

try:
    hojas = client.openall()
    if hojas:
        st.success("✅ Hojas accesibles por la cuenta de servicio:")
        for hoja in hojas:
            st.write(f"📄 {hoja.title}")
    else:
        st.warning("⚠️ No se encontró ninguna hoja accesible. Verificá los permisos.")
except Exception as e:
    st.error(f"❌ Error al intentar acceder: {e}")
