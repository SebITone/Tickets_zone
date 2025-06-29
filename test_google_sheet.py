import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("🔗 Test de conexión a Google Sheets")

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(CREDS)

try:
    sheet = client.open("streamlit_tickets").worksheet("Hoja1")
    data = sheet.get_all_values()
    st.success("✅ Conexión exitosa a la hoja de cálculo")
    st.write(data)
except Exception as e:
    st.error(f"❌ Error al acceder a la hoja: {e}")
