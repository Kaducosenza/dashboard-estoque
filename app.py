import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Dashboard de Estoque", layout="wide")

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
<style>
.main {background-color: #f5f7fa;}
.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.title("📦 Dashboard de Otimização de Estoque")

# =========================
# DADOS
# =========================
np.random.seed(42)

produtos = [f"Produto_{i}" for i in range(1, 51)]
categorias = ["Eletrônico", "Alimento", "Limpeza", "Bebida", "Vestuário"]

data = {
    "Produto": produtos,
    "Categoria": np.random.choice(categorias, 50),
    "Estoque Atual": np.random.randint(20, 1000, 50),
    "Estoque Minimo": np.random.randint(10, 200, 50),
    "Consumo Medio Mensal": np.random.randint(5, 300, 50),
    "Lead Time (dias)": np.random.randint(5, 30, 50),
    "Custo Unitario": np.round(np.random.uniform(5, 200, 50), 2),
}

df = pd.DataFrame(data)

# =========================
# CÁLCULOS
# =========================
df["Cobertura_dias"] = (df["Estoque Atual"] / df["Consumo Medio Mensal"]) * 30
df["Estoque_Seguranca"] = df["Consumo Medio Mensal"] * (df["Lead Time (dias)"] / 30)

def classificar(row):
    if row["Estoque Atual"] < row["Estoque_Seguranca"]:
        return "Ruptura"
    elif row["Cobertura_dias"] > 120:
        return "Excesso"
    else:
        return "Saudavel"

df["Status"] = df.apply(classificar, axis=1)
df["Valor Estoque"] = df["Estoque Atual"] * df["Custo Unitario"]

# =========================
# MACHINE LEARNING
# =========================
X = df[["Lead Time (dias)"]]
y = df["Consumo Medio Mensal"]

modelo = LinearRegression()
modelo.fit(X, y)

df["Previsao_Consumo"] = modelo.predict(X)

# =========================
# FILTRO
# =========================
categoria = st.selectbox("Filtrar por Categoria", ["Todas"] + list(df["Categoria"].unique()))

if categoria != "Todas":
    df = df[df["Categoria"] == categoria]

# =========================
# KPIs
# =========================
total = df["Valor Estoque"].sum()
excesso = df[df["Status"] == "Excesso"]["Valor Estoque"].sum()
ruptura = df[df["Status"] == "Ruptura"]["Valor Estoque"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Total", f"R$ {total:,.0f}")
col2.metric("📦 Excesso", f"R$ {excesso:,.0f}")
col3.metric("⚠️ Ruptura", f"R$ {ruptura:,.0f}")

# =========================
# GRÁFICOS
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição por Status")
    resumo = df.groupby("Status")["Valor Estoque"].sum()
    fig, ax = plt.subplots()
    resumo.plot(kind="bar", ax=ax)
    ax.set_ylabel("Valor (R$)")
    st.pyplot(fig)

with col2:
    st.subheader("Top 10 Produtos")
    top10 = df.sort_values(by="Valor Estoque", ascending=False).head(10)
    fig2, ax2 = plt.subplots()
    ax2.barh(top10["Produto"], top10["Valor Estoque"])
    ax2.invert_yaxis()
    st.pyplot(fig2)

# =========================
# ALERTAS
# =========================
st.subheader("🚨 Alertas de Ruptura")

ruptura_df = df[df["Status"] == "Ruptura"]

if not ruptura_df.empty:
    st.error(f"{len(ruptura_df)} produtos com risco de ruptura!")
    st.dataframe(ruptura_df[["Produto", "Estoque Atual", "Estoque_Seguranca"]])
else:
    st.success("Nenhum risco de ruptura identificado")

# =========================
# PREVISÃO
# =========================
st.subheader("📈 Previsão de Consumo")

st.dataframe(df[["Produto", "Consumo Medio Mensal", "Previsao_Consumo"]])

# =========================
# INSIGHTS
# =========================
st.subheader("💡 Insights Automáticos")

if excesso > ruptura:
    st.warning("Grande parte do capital está em excesso de estoque. Oportunidade clara de redução de custos.")
else:
    st.info("Atenção maior para risco de ruptura.")

# =========================
# TABELA FINAL
# =========================
st.subheader("Tabela Completa")
st.dataframe(df)