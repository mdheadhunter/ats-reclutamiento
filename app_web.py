import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# CONFIG
st.set_page_config(
    page_title="MD Headhunter ATS",
    page_icon="💼",
    layout="wide"
)

# CSS PREMIUM
st.markdown("""
<style>

.main {
    background-color: #f4f6f9;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

h1, h2, h3 {
    color: #111827;
}

.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 45px;
    border: none;
    background-color: #2563eb;
    color: white;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #1d4ed8;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# LOGIN
USUARIO = "admin"
PASSWORD = "1234"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
        <h1 style='text-align:center;'>💼 MD Headhunter</h1>
        <p style='text-align:center;'>ATS Recruitment System</p>
        </div>
        """, unsafe_allow_html=True)

        usuario = st.text_input("👤 Usuario")
        password = st.text_input("🔒 Contraseña", type="password")

        if st.button("Ingresar"):

            if usuario == USUARIO and password == PASSWORD:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    st.stop()

# BASE
os.makedirs("cvs_guardados", exist_ok=True)

if os.path.exists("candidatos.json"):
    with open("candidatos.json", "r") as f:
        candidatos = json.load(f)
else:
    candidatos = []

def guardar():
    with open("candidatos.json", "w") as f:
        json.dump(candidatos, f)

def leer_pdf(file):
    texto = ""
    lector = PyPDF2.PdfReader(file)

    for p in lector.pages:
        texto += p.extract_text() or ""

    return texto.lower()

# SIDEBAR
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    width=120
)

st.sidebar.title("MD Headhunter")

menu = st.sidebar.radio(
    "📌 Menú",
    ["Dashboard", "Evaluar CVs", "Pipeline"]
)

# DASHBOARD
if menu == "Dashboard":

    st.title("📊 Dashboard ATS")

    total = len(candidatos)
    aptos = sum(1 for c in candidatos if c["estado"] == "Apto")
    entrevistas = sum(1 for c in candidatos if c["estado"] == "Entrevista")
    rechazados = sum(1 for c in candidatos if c["estado"] == "Rechazado")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h2>{total}</h2>
        <p>Total</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <h2>{aptos}</h2>
        <p>Aptos</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
        <h2>{entrevistas}</h2>
        <p>Entrevistas</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
        <h2>{rechazados}</h2>
        <p>Rechazados</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # GRÁFICA
    fig, ax = plt.subplots()

    estados = ["Apto", "Entrevista", "Rechazado"]
    valores = [aptos, entrevistas, rechazados]

    ax.bar(estados, valores)

    st.pyplot(fig)

# EVALUAR
elif menu == "Evaluar CVs":

    st.title("🧠 Evaluación Inteligente")

    vacante = st.text_area(
        "📄 Descripción de vacante",
        height=200
    )

    archivos = st.file_uploader(
        "📂 Subir CVs PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("🚀 Analizar candidatos"):

        if not vacante:
            st.warning("Agrega descripción de vacante")

        else:

            for archivo in archivos:

                texto_cv = leer_pdf(archivo)

                textos = [vacante.lower(), texto_cv]

                vec = TfidfVectorizer().fit_transform(textos)

                sim = cosine_similarity(
                    vec[0:1],
                    vec[1:2]
                )[0][0]

                score = round(sim * 100, 2)

                estado = (
                    "Apto"
                    if score > 70
                    else "Medio"
                    if score > 40
                    else "Rechazado"
                )

                candidatos.append({
                    "nombre": archivo.name,
                    "score": score,
                    "estado": estado
                })

                st.success(
                    f"{archivo.name} analizado → {score}%"
                )

            guardar()

# PIPELINE
elif menu == "Pipeline":

    st.title("📋 Pipeline de Reclutamiento")

    buscar = st.text_input("🔍 Buscar candidato")

    filtro = st.selectbox(
        "📌 Filtrar",
        ["Todos", "Apto", "Entrevista", "Rechazado", "Medio"]
    )

    datos = []

    for c in candidatos:

        if buscar.lower() in c["nombre"].lower():

            if filtro == "Todos" or c["estado"] == filtro:

                datos.append(c)

                with st.container():

                    st.markdown(f"""
                    <div class="card">
                    <h4>{c['nombre']}</h4>
                    <p>Score: {c['score']}%</p>
                    <p>Estado: {c['estado']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True)
