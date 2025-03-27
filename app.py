
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
from scipy.integrate import cumtrapz
from io import BytesIO
from docx import Document
from docx.shared import Inches
import base64

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
        q_max_real = (np.max(consumo) / dias_mes) / tempo_dia * 1000

        st.header("3. Resultados")
        st.metric("Consumo Referencial (m³)", f"{consumo_ref:,.0f}")
        st.metric("Vazão Média (L/s)", f"{q_med:.2f}")
        st.metric("Vazão Máx. Diária (L/s)", f"{q_max_dia:.2f}")
        st.metric("Vazão Máx. Horária (L/s)", f"{q_max_hora:.2f}")
        st.metric("Vazão Máxima Dia e Hora (L/s)", f"{q_max_real:.2f}")

        # --- Gráfico de densidade ---
        st.header("4. Gráfico de Distribuição")
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.histplot(consumo, kde=True, stat="density", color="skyblue", edgecolor="black", bins=12, ax=ax1)

        x_vals = np.linspace(min(consumo), max(consumo), 1000)
        media, desvio = np.mean(consumo), np.std(consumo)
        normal_curve = norm.pdf(x_vals, loc=media, scale=desvio)
        ax1.plot(x_vals, normal_curve, color='red', linestyle='--', label='Distribuição Normal')

        ax1.axvline(consumo_ref, color='black', linestyle=':', label=f'{percentil}% ≈ {consumo_ref:,.0f} m³')
        ax1.set_xlabel("Consumo mensal (m³)")
        ax1.set_ylabel("Densidade estimada")
        ax1.set_title("Distribuição do Consumo com KDE e Normal")
        ax1.legend()
        st.pyplot(fig1)

        # --- Gráfico CDF KDE vs Normal ---
        st.header("5. Comparação das CDFs")
        kde = sns.kdeplot(consumo, bw_adjust=1)
        kde_y = kde.get_lines()[0].get_ydata()
        kde_x = kde.get_lines()[0].get_xdata()
        plt.clf()
        cdf_kde = cumtrapz(kde_y, kde_x, initial=0)
        cdf_norm = norm.cdf(kde_x, loc=media, scale=desvio)

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(kde_x, cdf_kde, label='CDF da KDE', color='blue')
        ax2.plot(kde_x, cdf_norm, label='CDF da Normal', color='red', linestyle='--')
        ax2.set_title("Funções de Distribuição Acumulada (CDF)\nKDE vs Distribuição Normal")
        ax2.set_xlabel("Consumo mensal de água (m³)")
        ax2.set_ylabel("Probabilidade acumulada")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)

        # --- Exportar para Word ---
        st.header("6. Exportar Resultados")
        if st.button("Gerar Relatório em Word"):
            doc = Document()
            doc.add_heading("Relatório de Consumo Referencial", 0)
            doc.add_paragraph(f"Percentil de projeto: {percentil}%")
            doc.add_paragraph(f"Consumo referencial: {consumo_ref:,.0f} m³")
            doc.add_paragraph(f"Vazão média: {q_med:.2f} L/s")
            doc.add_paragraph(f"Vazão máx. diária: {q_max_dia:.2f} L/s")
            doc.add_paragraph(f"Vazão máx. horária: {q_max_hora:.2f} L/s")
            doc.add_paragraph(f"Vazão máxima dia e hora observada: {q_max_real:.2f} L/s")

            img_bytes1 = BytesIO()
            fig1.savefig(img_bytes1, format='png')
            doc.add_picture(BytesIO(img_bytes1.getvalue()), width=Inches(5.5))

            img_bytes2 = BytesIO()
            fig2.savefig(img_bytes2, format='png')
            doc.add_picture(BytesIO(img_bytes2.getvalue()), width=Inches(5.5))

            buffer = BytesIO()
            doc.save(buffer)
            b64 = base64.b64encode(buffer.getvalue()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="relatorio_consumo.docx">📄 Baixar Relatório Word</a>'
            st.markdown(href, unsafe_allow_html=True)

    else:
        st.error("O arquivo CSV deve conter pelo menos duas colunas: Mês e Consumo.")
else:
    st.info("Aguardando upload do arquivo CSV com dados de consumo.")
