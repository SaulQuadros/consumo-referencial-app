
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Consumo Referencial", layout="centered")
st.title("🔹 Cálculo do Consumo Referencial Mensal de Água")

st.markdown("""
Este aplicativo permite calcular o **consumo mensal de referência** com base em dados históricos
para sistemas de abastecimento de água, utilizando **percentis estatísticos**.
""")

# --- Entrada de dados ---
st.header("1. Dados de Consumo Mensal")
uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV com os dados de consumo (em m³)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if df.shape[1] >= 2:
        df.columns = ['Mês', 'Consumo (m³)']
        st.success("Arquivo carregado com sucesso!")
        st.dataframe(df)

        # --- Parâmetros do projeto ---
        st.header("2. Parâmetros do Projeto")
        percentil = st.slider("Percentil de Projeto (%)", 50, 99, 95)
        dias_mes = st.number_input("Número de dias do mês", min_value=1, max_value=31, value=30)
        tempo_dia = st.number_input("Tempo diário (segundos)", min_value=1, value=86400)
        k1 = st.number_input("Coeficiente de máx. diária (K1)", min_value=1.0, value=1.4)
        k2 = st.number_input("Coeficiente de máx. horária (K2)", min_value=1.0, value=2.0)

        # --- Cálculos ---
        consumo = df['Consumo (m³)'].values
        consumo_ref = np.percentile(consumo, percentil)
        q_med = (consumo_ref / dias_mes) / tempo_dia * 1000  # em L/s
        q_max_dia = q_med * k1
        q_max_hora = q_med * k2

        st.header("3. Resultados")
        st.metric("Consumo Referencial (m³)", f"{consumo_ref:,.0f}")
        st.metric("Vazão Média (L/s)", f"{q_med:.2f}")
        st.metric("Vazão Máx. Diária (L/s)", f"{q_max_dia:.2f}")
        st.metric("Vazão Máx. Horária (L/s)", f"{q_max_hora:.2f}")

        # --- Gráfico ---
        st.header("4. Gráfico de Distribuição")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(consumo, kde=True, stat="density", color="skyblue", edgecolor="black", bins=12, ax=ax)
        ax.axvline(consumo_ref, color='red', linestyle='--', label=f'{percentil}% ≈ {consumo_ref:,.0f} m³')
        ax.set_xlabel("Consumo mensal (m³)")
        ax.set_ylabel("Densidade estimada")
        ax.set_title("Distribuição do Consumo com Percentil Destacado")
        ax.legend()
        st.pyplot(fig)

    else:
        st.error("O arquivo CSV deve conter pelo menos duas colunas: Mês e Consumo.")
else:
    st.info("Aguardando upload do arquivo CSV com dados de consumo.")
