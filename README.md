# 💧 Consumo Referencial Mensal de Água – App Streamlit

Este aplicativo permite calcular o **consumo mensal de referência** com base em dados históricos, aplicando conceitos estatísticos como **percentis, densidade KDE** e **distribuição normal**.

Ideal para dimensionamento de **sistemas de abastecimento de água tratada**.

---

## 🚀 Funcionalidades

- 📤 Upload de arquivo `.csv` com dados históricos de consumo
- 📊 Cálculo automático dos seguintes parâmetros:
  - Consumo referencial por percentil (ex: 95%)
  - Desvio padrão dos dados
  - Vazão média (L/s)
  - Vazão máxima diária e horária (por coeficiente)
  - Vazão máxima real observada
- 📈 Gráficos:
  - Curva de distribuição KDE + Normal (PDF)
  - Curva de distribuição acumulada (CDF) comparativa
- 📄 Geração automática de relatório em **formato Word (.docx)** com resultados e gráficos

---

## 🧾 Formato do arquivo de entrada

O arquivo `.csv` deve conter duas colunas:

```csv
Mês,Consumo (m³)
Jan/2021,456000
Fev/2021,470000
...
```

---

## 🌐 Acesse o app online

👉 [Clique aqui para acessar o app no Streamlit](https://consumo-referencial.streamlit.app)

---

## 🛠️ Instalação local (opcional)

```bash
git clone https://github.com/seu-usuario/consumo-referencial-app.git
cd consumo-referencial-app
pip install -r requirements.txt
streamlit run app.py
```

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT.
