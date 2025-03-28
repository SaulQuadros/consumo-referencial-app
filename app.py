import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, shapiro, normaltest, kstest
from io import BytesIO
from docx import Document
from docx.shared import Inches
    import base64
    import os

    st.set_page_config(page_title="Consumo Referencial", layout="centered")

    # --- Menu de Navegação ---
    aba = st.sidebar.radio("Navegação", ["📊 Cálculo do Consumo", "📘 Sobre o Modelo Estatístico"])

    # --- Aba 1: Cálculo do Consumo ---
    if aba == "📊 Cálculo do Consumo":
        st.title("Cálculo do Consumo Referencial")

        st.markdown("""
        Este aplicativo permite calcular o **consumo mensal de referência** com base em dados históricos
        para sistemas de abastecimento de água, utilizando **percentis estatísticos**.

        > ℹ️ Os dados de consumo mensal podem ser provenientes de **micromedições** (hidrômetros) ou **macromedições** (na saída do reservatório).  
        > É responsabilidade do usuário conhecer a origem dos dados fornecidos.
        """)

        st.header("1. Dados de Consumo Mensal")
        uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV com os dados de consumo (em m³)", type="csv")

        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if df.shape[1] >= 2:
                df.columns = ['Mês', 'Consumo (m³)']
                st.success("Arquivo carregado com sucesso!")
                st.dataframe(df)

                st.header("2. Parâmetros do Projeto")
                percentil = st.slider("Percentil de Projeto (%)", 50, 99, 95)
                dias_mes = st.number_input("Número de dias do mês", min_value=1, max_value=31, value=30)
                tempo_dia = st.number_input("Tempo diário (segundos)", min_value=1, value=86400)
                k1 = st.number_input("Coeficiente de máx. diária (K1)", min_value=1.0, value=1.4)
                k2 = st.number_input("Coeficiente de máx. horária (K2)", min_value=1.0, value=2.0)
                modelo = st.selectbox("Modelo Estatístico", ["KDE", "Distribuição Normal"])

                consumo = df['Consumo (m³)'].values
                consumo_ref = np.percentile(consumo, percentil)
                media = np.mean(consumo)
                desvio_padrao = np.std(consumo)
                q_med = (consumo_ref / dias_mes) / tempo_dia * 1000
                q_max_dia = q_med * k1
                q_max_hora = q_med * k2
                q_max_real = (np.max(consumo) / dias_mes) / tempo_dia * 1000

                st.header("3. Resultados")
                st.metric("Consumo Referencial (m³)", f"{consumo_ref:,.0f}".replace(",", "."))
                st.metric("Desvio Padrão (m³)", f"{desvio_padrao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.metric("Vazão Média (L/s)", f"{q_med:.2f}".replace(".", ","))
                st.metric("Vazão Máx. Diária (L/s)", f"{q_max_dia:.2f}".replace(".", ","))
                st.metric("Vazão Máx. Horária (L/s)", f"{q_max_hora:.2f}".replace(".", ","))
                st.metric("Vazão Máxima Dia e Hora (L/s)", f"{q_max_real:.2f}".replace(".", ","))

                # Gráfico de distribuição com curva KDE e normal
                st.header("4. Gráfico de Distribuição")
                fig1, ax1 = plt.subplots(figsize=(10, 5))
                sns.histplot(consumo, kde=(modelo == "KDE"), stat="density", color="skyblue", edgecolor="black", bins=12, ax=ax1)

                x_vals = np.linspace(min(consumo), max(consumo), 1000)
                normal_curve = norm.pdf(x_vals, loc=media, scale=desvio_padrao)
                ax1.plot(x_vals, normal_curve, color='red', linestyle='--', label='Distribuição Normal')
                ax1.axvline(consumo_ref, color='black', linestyle=':', label=f'{percentil}% ≈ {consumo_ref:,.0f} m³')
                ax1.set_xlabel("Consumo mensal (m³)")
                ax1.set_ylabel("Densidade estimada")
                ax1.set_title("Distribuição do Consumo com KDE e Normal")
                ax1.legend()
                st.pyplot(fig1)

                # Gráfico CDF
                st.header("5. Comparação das CDFs")
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
                ax2.set_title("Funções de Distribuição Acumulada (CDF)
KDE vs Distribuição Normal")
                ax2.set_xlabel("Consumo mensal de água (m³)")
                ax2.set_ylabel("Probabilidade acumulada")
                ax2.legend()
                ax2.grid(True)
                st.pyplot(fig2)

                # Testes de normalidade
                st.header("6. Testes de Normalidade")
                stat1, p1 = shapiro(consumo)
                stat2, p2 = normaltest(consumo)
                stat3, p3 = kstest(consumo, 'norm', args=(media, desvio_padrao))

                interp = lambda p: "✅ Dados seguem distribuição normal." if p > 0.05 else "⚠️ Dados não seguem distribuição normal."

                st.write(f"**Shapiro-Wilk**: Estatística = {stat1:.3f}, p-valor = {p1:.3f} → {interp(p1)}")
                st.write(f"**D'Agostino e Pearson**: Estatística = {stat2:.3f}, p-valor = {p2:.3f} → {interp(p2)}")
                st.write(f"**Kolmogorov-Smirnov (KS)**: Estatística = {stat3:.3f}, p-valor = {p3:.3f} → {interp(p3)}")

    else:
        st.info("Aguardando upload do arquivo CSV com dados de consumo.")

    # --- Aba 2: Sobre o Modelo Estatístico ---
    elif aba == "📘 Sobre o Modelo Estatístico":
        st.title("📘 Sobre o Modelo Estatístico")
        st.markdown("Visualize abaixo o conteúdo técnico referente ao modelo estatístico utilizado.")
        try:
            paginas = sorted([f for f in os.listdir("docs") if f.endswith(".png")])
            idx = st.selectbox("Selecionar página:", range(len(paginas)), format_func=lambda x: f"Página {x+1}")
            st.image("docs/" + paginas[idx], use_column_width=True)
        except Exception as e:
            st.error("Erro ao carregar imagens da pasta 'docs/'. Verifique se elas estão no repositório.")
