
import streamlit as st
import os

# Inicializa o índice da página
if "pagina_index" not in st.session_state:
    st.session_state.pagina_index = 0

# Lista e ordena as imagens da pasta docs/
paginas = sorted([f for f in os.listdir("docs") if f.endswith(".png")])

# Página atual
pagina_atual = paginas[st.session_state.pagina_index]

st.title("📘 Sobre o Modelo Estatístico")
st.markdown("Visualize abaixo o conteúdo técnico referente ao modelo estatístico utilizado.")

# Exibe a imagem da página atual
st.image(f"docs/{pagina_atual}", use_column_width=True)

# Navegação com botões
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.session_state.pagina_index > 0:
        if st.button("⬅️ Página Anterior"):
            st.session_state.pagina_index -= 1
with col3:
    if st.session_state.pagina_index < len(paginas) - 1:
        if st.button("Próxima Página ➡️"):
            st.session_state.pagina_index += 1
