import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import os
import json
import matplotlib.pyplot as plt

# 📂 Config
os.makedirs("cvs_guardados", exist_ok=True)

# 🔐 LOGIN SIMPLE
USUARIO = "admin"
PASSWORD = "1234"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login ATS")

    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if user == USUARIO and pwd == PASSWORD:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

    st.stop()

# 📂 Cargar datos
if os.path.exists("candidatos.json"):
    with open("candidatos.json", "r") as f:
        candidatos = json.load(f)
else:
    candidatos = []

def guardar():
    with open("candidatos.json", "w") as f:
        json.dump(candidatos, f)

# 📄 Leer PDF
def leer_pdf(file):
    texto = ""
    lector = PyPDF2.PdfReader(file)
    for p in lector.pages:
        texto += p.extract_text() or ""
    return texto.lower()

# UI
st.title("💼 MD Headhunter | ATS PRO WEB")

vacante = st.text_area("📄 Descripción de vacante")

archivos = st.file_uploader("📂 Subir CVs", type=["pdf"], accept_multiple_files=True)

# 🧠 Evaluar
if st.button("🧠 Evaluar candidatos"):

    if not vacante:
        st.warning("Agrega vacante")
    else:
        for archivo in archivos:
            texto_cv = leer_pdf(archivo)

            textos = [vacante.lower(), texto_cv]
            vec = TfidfVectorizer().fit_transform(textos)
            sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
            score = round(sim * 100, 2)

            estado = "APTO" if score > 70 else "MEDIO" if score > 40 else "NO APTO"

            candidatos.append({
                "nombre": archivo.name,
                "score": score,
                "estado": "Postulado"
            })

            st.success(f"{archivo.name} → {score}% ({estado})")

        guardar()

# 📊 DASHBOARD
st.subheader("📊 Dashboard")

total = len(candidatos)
aptos = sum(1 for c in candidatos if c["estado"] == "Apto")
entrevista = sum(1 for c in candidatos if c["estado"] == "Entrevista")
rechazados = sum(1 for c in candidatos if c["estado"] == "Rechazado")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", total)
col2.metric("Aptos", aptos)
col3.metric("Entrevista", entrevista)
col4.metric("Rechazados", rechazados)

# 📈 GRÁFICA
st.subheader("📈 Gráfica")

fig, ax = plt.subplots()
estados = ["Apto", "Entrevista", "Rechazado"]
valores = [aptos, entrevista, rechazados]

ax.bar(estados, valores)
ax.set_title("Estado de candidatos")

st.pyplot(fig)

# 🔍 BUSCADOR
busqueda = st.text_input("🔍 Buscar candidato")

# 📊 FILTRO
filtro = st.selectbox("📊 Filtro", ["Todos", "Postulado", "Apto", "Entrevista", "Rechazado"])

# 📋 PIPELINE
st.subheader("📋 Pipeline")

for c in candidatos:
    if busqueda.lower() in c["nombre"].lower():
        if filtro == "Todos" or c["estado"] == filtro:

            col1, col2 = st.columns([3,1])

            col1.write(f"{c['nombre']} - {c['estado']}")

            if col2.button("Apto", key=c["nombre"]+"a"):
                c["estado"] = "Apto"
            if col2.button("Entrevista", key=c["nombre"]+"e"):
                c["estado"] = "Entrevista"
            if col2.button("Rechazado", key=c["nombre"]+"r"):
                c["estado"] = "Rechazado"

guardar()