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

# Ajuste de layout/título da página
st.set_page_config(page_title="Consumo Referencial", layout="centered")

# Navegação por abas
aba = st.sidebar.radio("Navegar para:", ["🧮 Cálculo do Consumo", "📘 Sobre o Modelo Estatístico"])

if aba == "🧮 Cálculo do Consumo":
    st.title("Cálculo do Consumo Referencial")
    st.markdown("🔧 Interface de cálculo do consumo (conteúdo ocultado aqui para simplicidade).")

    st.header("1. Dados de Consumo Mensal")
    uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV com os dados de consumo (em m³)", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if df.shape[1] >= 2:
            df.columns = ['Mês', 'Consumo (m³)']
            st.success("Arquivo carregado com sucesso!")
            st.dataframe(df)

            st.markdown("""
            ℹ️ Os dados históricos de consumo mensal podem ter origem em micromedições (hidrômetros) ou macromedições (na saída do reservatório).
            É importante conhecer a origem dos dados para interpretar corretamente os resultados.
            """)

            st.header("2. Parâmetros do Projeto")
            modelo = st.selectbox("Modelo Estatístico", ["KDE", "Distribuição Normal"])
            percentil = st.slider("Percentil de Projeto (%)", 50, 99, 95)
            dias_mes = st.number_input("Número de dias do mês", min_value=1, max_value=31, value=30)
            # Valor fixo para tempo diário (86400 s)
            tempo_dia = 86400

            k1 = st.number_input("Coeficiente de máx. diária (K1)", min_value=1.0, value=1.4)
            k2 = st.number_input("Coeficiente de máx. horária (K2)", min_value=1.0, value=2.0)

            consumo = df['Consumo (m³)'].values

            # Cálculo do consumo referencial
            if modelo == "KDE":
                kde = sns.kdeplot(consumo, bw_adjust=1)
                kde_y = kde.get_lines()[0].get_ydata()
                kde_x = kde.get_lines()[0].get_xdata()
                plt.clf()
                cdf_kde = np.cumsum(kde_y)
                cdf_kde = cdf_kde / cdf_kde[-1]
                consumo_ref = kde_x[np.searchsorted(cdf_kde, percentil / 100)]
            else:
                consumo_ref = np.percentile(consumo, percentil)

            # Cálculo das vazões
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

            st.write(f"**Shapiro-Wilk**: Estatística = {stat_sw:.3f}, p-valor = {p_sw:.3f} — {interpreta(p_sw)}")
            st.write(f"**D'Agostino e Pearson**: Estatística = {stat_dp:.3f}, p-valor = {p_dp:.3f} — {interpreta(p_dp)}")
            st.write(f"**Kolmogorov-Smirnov (KS)**: Estatística = {stat_ks:.3f}, p-valor = {p_ks:.3f} — {interpreta(p_ks)}")

            st.header("5. Gráfico de Distribuição")
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

            st.header("6. Funções de Distribuição Acumulada")
            kde = sns.kdeplot(consumo, bw_adjust=1)
            kde_y = kde.get_lines()[0].get_ydata()
            kde_x = kde.get_lines()[0].get_xdata()
            plt.clf()
            cdf_kde = np.cumsum(kde_y)
            cdf_kde = cdf_kde / cdf_kde[-1]
            cdf_norm = norm.cdf(kde_x, loc=media, scale=desvio_padrao)

            fig2, ax2 = plt.subplots(figsize=(8, 5))
            ax2.plot(kde_x, cdf_kde, label='CDF da KDE', color='blue')
            ax2.plot(kde_x, cdf_norm, label='CDF da Normal', color='red', linestyle='--')
            ax2.set_title("Funções de Distribuição Acumulada (CDF) KDE vs Distribuição Normal")
            ax2.set_xlabel("Consumo mensal de água (m³)")
            ax2.set_ylabel("Probabilidade acumulada")
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)

elif aba == "📘 Sobre o Modelo Estatístico":
    st.title("📘 Sobre o Modelo Estatístico")
    st.write("Visualize abaixo o relatório completo em PDF.")

    # Nome do arquivo PDF
    pdf_file = "03_Estatistica_2025.pdf"

    if os.path.exists(pdf_file):
        # Lê o arquivo PDF e o converte para base64
        with open(pdf_file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # Cria um iframe para exibir o PDF
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.warning(f"Arquivo PDF '{pdf_file}' não encontrado no diretório atual.")

