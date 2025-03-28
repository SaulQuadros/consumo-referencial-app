#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, shapiro, normaltest, kstest
import os
import base64

from io import BytesIO
from docx import Document
from docx.shared import Inches

st.set_page_config(page_title="Consumo Referencial", layout="centered")

# Persistência do DataFrame
if "df_consumo" not in st.session_state:
    st.session_state.df_consumo = None

aba = st.sidebar.radio("Navegar para:", ["🧮 Cálculo do Consumo", "📘 Sobre o Modelo Estatístico"])

if aba == "🧮 Cálculo do Consumo":
    st.title("Cálculo do Consumo Referencial")

    st.header("1. Dados de Consumo Mensal")
    if st.session_state.df_consumo is None:
        uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV (2 colunas: Mês, Consumo (m³))", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if df.shape[1] >= 2:
                    df.columns = ['Mês', 'Consumo (m³)']
                    st.session_state.df_consumo = df
                    st.success("Arquivo carregado com sucesso!")
                else:
                    st.error("O arquivo precisa ter pelo menos duas colunas.")
            except Exception as e:
                st.error(f"Erro ao ler o CSV: {e}")
    else:
        st.info("Arquivo CSV já carregado.")
    
    if st.session_state.df_consumo is not None:
        df = st.session_state.df_consumo
        st.dataframe(df)

        st.header("2. Parâmetros do Projeto")
        modelo = st.selectbox("Modelo Estatístico", ["KDE", "Distribuição Normal"])
        percentil = st.slider("Percentil de Projeto (%)", 50, 99, 95)
        dias_mes = st.number_input("Número de dias do mês", min_value=1, max_value=31, value=30)
        tempo_dia = 86400
        k1 = st.number_input("Coeficiente de máx. diária (K1)", min_value=1.0, value=1.4)
        k2 = st.number_input("Coeficiente de máx. horária (K2)", min_value=1.0, value=2.0)

        consumo = df['Consumo (m³)'].values

        # 1) Cálculo do consumo referencial
        if modelo == "KDE":
            # Cria uma figura "temporária" só para gerar a curva e extrair os dados
            fig_temp, ax_temp = plt.subplots()
            kde = sns.kdeplot(consumo, bw_adjust=1, ax=ax_temp)
            kde_y = kde.get_lines()[0].get_ydata()
            kde_x = kde.get_lines()[0].get_xdata()
            plt.close(fig_temp)  # Fechamos essa figura temporária

            cdf_kde = np.cumsum(kde_y)
            cdf_kde = cdf_kde / cdf_kde[-1]
            consumo_ref = kde_x[np.searchsorted(cdf_kde, percentil / 100)]
        else:
            consumo_ref = np.percentile(consumo, percentil)

        # 2) Vazões
        q_med = (consumo_ref / dias_mes) / tempo_dia * 1000
        q_max_dia = q_med * k1
        q_max_hora = q_med * k2
        q_max_real = q_med * k1 * k2

        desvio_padrao = np.std(consumo)
        media = np.mean(consumo)

        st.header("3. Resultados")
        st.metric("Consumo Referencial (m³)", f"{consumo_ref:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.metric("Desvio Padrão (m³)", f"{desvio_padrao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.metric("Vazão Média (L/s)", f"{q_med:.2f}".replace(".", ","))
        st.metric("Vazão Máx. Diária (L/s)", f"{q_max_dia:.2f}".replace(".", ","))
        st.metric("Vazão Máx. Horária (L/s)", f"{q_max_hora:.2f}".replace(".", ","))
        st.metric("Vazão Máx. Dia+Hora (L/s)", f"{q_max_real:.2f}".replace(".", ","))

        st.header("4. Testes de Normalidade")
        stat_sw, p_sw = shapiro(consumo)
        stat_dp, p_dp = normaltest(consumo)
        stat_ks, p_ks = kstest(consumo, 'norm', args=(media, desvio_padrao))

        def interpreta(p):
            return "✔️ Aceita a hipótese de normalidade." if p > 0.05 else "❌ Rejeita a hipótese de normalidade."

        txt_sw = f"Shapiro-Wilk: Estatística = {stat_sw:.3f}, p-valor = {p_sw:.3f} — {interpreta(p_sw)}"
        txt_dp = f"D'Agostino e Pearson: Estatística = {stat_dp:.3f}, p-valor = {p_dp:.3f} — {interpreta(p_dp)}"
        txt_ks = f"Kolmogorov-Smirnov (KS): Estatística = {stat_ks:.3f}, p-valor = {p_ks:.3f} — {interpreta(p_ks)}"

        st.write(f"**{txt_sw}**")
        st.write(f"**{txt_dp}**")
        st.write(f"**{txt_ks}**")

        # 5) Gráfico de Distribuição (fig1)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.histplot(consumo, kde=True, stat="density", color="skyblue", edgecolor="black", bins=12, ax=ax1)
        x_vals = np.linspace(min(consumo), max(consumo), 1000)
        normal_curve = norm.pdf(x_vals, loc=media, scale=desvio_padrao)
        ax1.plot(x_vals, normal_curve, color='red', linestyle='--', label='Distribuição Normal')
        ax1.axvline(consumo_ref, color='black', linestyle=':', label=f'{percentil}% ≈ {consumo_ref:,.0f} m³')
        ax1.set_xlabel("Consumo mensal (m³)")
        ax1.set_ylabel("Densidade estimada")
        ax1.set_title("Distribuição do Consumo com KDE e Normal")
        ax1.legend()
        st.pyplot(fig1)

        # 6) Funções de Distribuição Acumulada (fig2)
        # Precisamos gerar novamente os dados do KDE sem sobrescrever fig1
        fig_temp2, ax_temp2 = plt.subplots()
        kde_plot = sns.kdeplot(consumo, bw_adjust=1, ax=ax_temp2)
        kde_y2 = kde_plot.get_lines()[0].get_ydata()
        kde_x2 = kde_plot.get_lines()[0].get_xdata()
        plt.close(fig_temp2)

        cdf_kde2 = np.cumsum(kde_y2)
        cdf_kde2 = cdf_kde2 / cdf_kde2[-1]
        cdf_norm = norm.cdf(kde_x2, loc=media, scale=desvio_padrao)

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(kde_x2, cdf_kde2, label='CDF da KDE', color='blue')
        ax2.plot(kde_x2, cdf_norm, label='CDF da Normal', color='red', linestyle='--')
        ax2.set_title("Funções de Distribuição Acumulada (CDF) KDE vs Distribuição Normal")
        ax2.set_xlabel("Consumo mensal de água (m³)")
        ax2.set_ylabel("Probabilidade acumulada")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)

        st.header("Relatório em Word")
        if st.button("Gerar Relatório Word"):
            doc = Document()
            doc.add_heading("Relatório de Consumo Referencial", 0)

            doc.add_heading("Parâmetros de Entrada", level=1)
            doc.add_paragraph(f"Modelo Estatístico: {modelo}")
            doc.add_paragraph(f"Percentil de Projeto: {percentil}%")
            doc.add_paragraph(f"Número de dias do mês: {dias_mes}")
            doc.add_paragraph(f"Tempo diário (s): {tempo_dia}")
            doc.add_paragraph(f"K1 (máx. diária): {k1}")
            doc.add_paragraph(f"K2 (máx. horária): {k2}")

            doc.add_heading("Resultados", level=1)
            doc.add_paragraph(f"Consumo Referencial (m³): {consumo_ref:,.0f}")
            doc.add_paragraph(f"Desvio Padrão (m³): {desvio_padrao:,.2f}")
            doc.add_paragraph(f"Vazão Média (L/s): {q_med:.2f}")
            doc.add_paragraph(f"Vazão Máx. Diária (L/s): {q_max_dia:.2f}")
            doc.add_paragraph(f"Vazão Máx. Horária (L/s): {q_max_hora:.2f}")
            doc.add_paragraph(f"Vazão Máx. Dia+Hora (L/s): {q_max_real:.2f}")

            doc.add_heading("Testes de Normalidade", level=1)
            doc.add_paragraph(txt_sw)
            doc.add_paragraph(txt_dp)
            doc.add_paragraph(txt_ks)

            # Salva fig1
            img_buffer1 = BytesIO()
            fig1.savefig(img_buffer1, format="png", dpi=150)
            img_buffer1.seek(0)
            doc.add_heading("Gráfico de Distribuição", level=1)
            doc.add_picture(img_buffer1, width=Inches(6))

            # Salva fig2
            img_buffer2 = BytesIO()
            fig2.savefig(img_buffer2, format="png", dpi=150)
            img_buffer2.seek(0)
            doc.add_heading("Funções de Distribuição Acumulada", level=1)
            doc.add_picture(img_buffer2, width=Inches(6))

            doc_buffer = BytesIO()
            doc.save(doc_buffer)
            doc_buffer.seek(0)

            st.download_button(
                label="Baixar Relatório Word",
                data=doc_buffer.getvalue(),
                file_name="Relatorio_Consumo.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

elif aba == "📘 Sobre o Modelo Estatístico":
    st.title("📘 Sobre o Modelo Estatístico")
    st.write("Clique no link abaixo para abrir o relatório PDF em uma nova aba:")
    pdf_file = "03_Estatistica_2025.pdf"
    if os.path.exists(pdf_file):
        pdf_link = f'<a href="{pdf_file}" target="_blank" rel="noopener noreferrer">Abrir Relatório PDF</a>'
        st.markdown(pdf_link, unsafe_allow_html=True)

        # Botão de download do PDF
        with open(pdf_file, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="Baixar PDF",
            data=pdf_bytes,
            file_name="03_Estatistica_2025.pdf",
            mime="application/pdf"
        )
    else:
        st.warning(f"Arquivo PDF '{pdf_file}' não encontrado no diretório atual.")


# In[ ]:




