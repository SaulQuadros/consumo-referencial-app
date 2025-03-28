
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, shapiro, normaltest, kstest
import os

st.set_page_config(page_title="Consumo Referencial", layout="wide")
aba = st.sidebar.radio("Navegação", ["🔍 Cálculo do Consumo", "📘 Sobre o Modelo Estatístico"])

if aba == "📘 Sobre o Modelo Estatístico":
    st.title("📘 Sobre o Modelo Estatístico")
    st.markdown("Visualize abaixo o conteúdo técnico referente ao modelo estatístico utilizado.")
    paginas = sorted([f for f in os.listdir("docs_img") if f.endswith(".png")])
    idx = st.number_input("Página", min_value=1, max_value=len(paginas), step=1) - 1
    st.image("docs_img/" + paginas[idx], use_column_width=True)

else:
    st.title("Cálculo do Consumo Referencial")
    st.markdown("Os dados históricos de consumo mensal utilizados podem ter origem em **micromedições** (como hidrômetros individuais) ou em **macromedições** (como sensores instalados na saída de reservatórios). É responsabilidade do usuário conhecer a natureza e origem dos dados que está fornecendo para a análise estatística.")

    st.header("1. Dados de Consumo Mensal")
    uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV com os dados de consumo (em m³)", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if df.shape[1] >= 2:
            df.columns = ['Mês', 'Consumo (m³)']
            consumo = df['Consumo (m³)'].values
            st.success("Arquivo carregado com sucesso!")
            st.dataframe(df)

            st.header("2. Parâmetros do Projeto")
            modelo = st.selectbox("Modelo Estatístico", ["KDE", "Distribuição Normal"])
            percentil = st.slider("Percentil de Projeto (%)", 50, 99, 95)
            dias_mes = st.number_input("Número de dias do mês", min_value=1, max_value=31, value=30)
            tempo_dia = st.number_input("Tempo diário (segundos)", min_value=1, value=86400)
            k1 = st.number_input("Coeficiente de máx. diária (K1)", min_value=1.0, value=1.4)
            k2 = st.number_input("Coeficiente de máx. horária (K2)", min_value=1.0, value=2.0)

            consumo_ref = np.percentile(consumo, percentil)
            q_med = (consumo_ref / dias_mes) / tempo_dia * 1000
            q_max_dia = q_med * k1
            q_max_hora = q_med * k2
            q_max_real = (np.max(consumo) / dias_mes) / tempo_dia * 1000
            desvio_padrao = np.std(consumo)
            media = np.mean(consumo)

            st.header("3. Resultados")
            col1, col2, col3 = st.columns(3)
            col1.metric("Consumo Referencial (m³)", "{:,.2f}".format(consumo_ref).replace(",", "X").replace(".", ",").replace("X", "."))
            col2.metric("Desvio Padrão (m³)", "{:,.2f}".format(desvio_padrao).replace(",", "X").replace(".", ",").replace("X", "."))
            col3.metric("Média (m³)", "{:,.2f}".format(media).replace(",", "X").replace(".", ",").replace("X", "."))

            col4, col5, col6 = st.columns(3)
            col4.metric("Vazão Média (L/s)", "{:,.2f}".format(q_med).replace(",", "X").replace(".", ",").replace("X", "."))
            col5.metric("Vazão Máx. Diária (L/s)", "{:,.2f}".format(q_max_dia).replace(",", "X").replace(".", ",").replace("X", "."))
            col6.metric("Vazão Máx. Horária (L/s)", "{:,.2f}".format(q_max_hora).replace(",", "X").replace(".", ",").replace("X", "."))

            st.metric("Vazão Máxima Dia e Hora (L/s)", "{:,.2f}".format(q_max_real).replace(",", "X").replace(".", ",").replace("X", "."))

            st.header("4. Testes de Normalidade")
            stat1, p1 = shapiro(consumo)
            stat2, p2 = normaltest(consumo)
            stat3, p3 = kstest(consumo, 'norm', args=(media, desvio_padrao))

            st.write(f"Shapiro-Wilk: Estatística = {stat1:.3f}, p-valor = {p1:.3f}")
            st.write(f"D'Agostino e Pearson: Estatística = {stat2:.3f}, p-valor = {p2:.3f}")
            st.write(f"Kolmogorov-Smirnov: Estatística = {stat3:.3f}, p-valor = {p3:.3f}")

            st.header("5. Gráfico de Distribuição")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.histplot(consumo, kde=(modelo=="KDE"), stat="density", color="skyblue", edgecolor="black", bins=12, ax=ax)

            x_vals = np.linspace(min(consumo), max(consumo), 1000)
            normal_curve = norm.pdf(x_vals, loc=media, scale=desvio_padrao)
            ax.plot(x_vals, normal_curve, color='red', linestyle='--', label='Distribuição Normal')
            ax.axvline(consumo_ref, color='black', linestyle=':', label=f'{percentil}% ≈ {consumo_ref:,.0f} m³')
            ax.set_xlabel("Consumo mensal (m³)")
            ax.set_ylabel("Densidade estimada")
            ax.set_title("Distribuição do Consumo")
            ax.legend()
            st.pyplot(fig)

        else:
            st.error("O arquivo CSV deve conter pelo menos duas colunas: Mês e Consumo.")
    else:
        st.info("Aguardando upload do arquivo CSV com dados de consumo.")
