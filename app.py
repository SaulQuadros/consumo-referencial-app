import streamlit as st
import os

st.set_page_config(page_title="Consumo Referencial", layout="centered")
aba = st.sidebar.radio("Navegação", ["🔍 Cálculo do Consumo", "📘 Sobre o Modelo Estatístico"])

if aba == "📘 Sobre o Modelo Estatístico":
    st.title("📘 Sobre o Modelo Estatístico")
    st.markdown("Navegue abaixo pelas seções extraídas do conteúdo PDF:")

    html_files = sorted([f for f in os.listdir("docs") if f.endswith(".html")])
    pagina = st.selectbox("Selecionar página:", html_files)
    if pagina:
        with open(os.path.join("docs", pagina), "r", encoding="utf-8") as f:
            html_content = f.read()
            st.components.v1.html(html_content, height=700, scrolling=True)
else:
    st.title("Cálculo do Consumo Referencial")
    st.write("🔧 Interface de cálculo do consumo (conteúdo ocultado aqui para simplicidade).")
