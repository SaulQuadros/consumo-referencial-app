
# 💧 Cálculo do Consumo Referencial Mensal de Água

Este aplicativo foi desenvolvido para auxiliar engenheiros e profissionais da área de saneamento no **dimensionamento de sistemas de abastecimento de água**, com base em **dados históricos mensais de consumo**.

---

## 📌 Funcionalidades

✅ Upload de arquivo CSV com dados de consumo mensal (colunas: `Mês`, `Consumo (m³)`)

✅ Cálculo do consumo referencial com base em **percentis estatísticos**

✅ Cálculo de:
- Vazão média (L/s)
- Vazão máxima diária (K1)
- Vazão máxima horária (K2)
- Vazão máxima dia e hora real observada
- Média e desvio padrão

✅ Seleção entre dois modelos estatísticos:
- **KDE (Kernel Density Estimation)**
- **Distribuição Normal**

✅ Comparação gráfica entre distribuições:
- Histograma + Curva KDE
- Curva da distribuição Normal
- CDF (Função de Distribuição Acumulada)

✅ Testes estatísticos de **normalidade**:
- Shapiro-Wilk
- D’Agostino e Pearson
- Kolmogorov-Smirnov

✅ Exportação de relatório completo em **Word (.docx)**

✅ Página "📘 Sobre o Modelo Estatístico", com conteúdo explicativo extraído de PDF

---

## 📁 Estrutura de Arquivos

```
📦 consumo_referencial_app
├── app.py
├── requirements.txt
├── docs_img/
│   ├── pagina_1.png
│   ├── pagina_2.png
│   └── ...
```

---

## 📥 Requisitos

Para rodar localmente:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📈 Observação sobre os dados

Os dados históricos de consumo mensal podem ter origem em:
- **Micromedições** (hidrômetros em domicílios)
- **Macromedições** (medição na saída do reservatório)

> ⚠️ É responsabilidade do usuário conhecer a natureza dos dados informados.

---

## 🛠️ Desenvolvido com:
- Python
- Streamlit
- Pandas, NumPy, Seaborn, Matplotlib, SciPy

---
