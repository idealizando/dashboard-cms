import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar os dados
df = pd.read_excel('data/Vendas_CM_Couto_2024_2025.xlsx')
df['Data Venda'] = pd.to_datetime(df['Data Venda'])

# Configuração da página
st.set_page_config(page_title="Dashboard CM Couto", layout="wide")
st.title("📊 Dashboard de Vendas - CM Couto")

# Sidebar - Filtros
st.sidebar.header("Filtros")
data_inicio = st.sidebar.date_input("Data Inicial", df['Data Venda'].min())
data_fim = st.sidebar.date_input("Data Final", df['Data Venda'].max())

# Aplicar filtros
filtro = (df['Data Venda'] >= pd.to_datetime(data_inicio)) & (df['Data Venda'] <= pd.to_datetime(data_fim))
df_filtrado = df[filtro]

# =========================
# 🔹 MÉTRICAS PRINCIPAIS
# =========================
col1, col2 = st.columns(2)
col1.metric("🛒 Total de Pedidos", df_filtrado.shape[0])
col2.metric("💵 Faturamento Líquido", f"R$ {df_filtrado['Valor Líquido (R$)'].sum():,.2f}")

st.markdown("---")

# =========================
# 📈 COMPARATIVO ANO A ANO
# =========================
df_filtrado['Ano'] = df_filtrado['Data Venda'].dt.year
vendas_por_ano = df_filtrado.groupby('Ano')['Valor Líquido (R$)'].sum()

if len(vendas_por_ano) >= 2:
    anos = sorted(vendas_por_ano.index)
    atual = vendas_por_ano[anos[-1]]
    anterior = vendas_por_ano[anos[-2]]
    variacao = ((atual - anterior) / anterior) * 100 if anterior else 0
else:
    atual = anterior = variacao = 0

st.subheader("📊 Comparativo com Ano Anterior")
col3, col4, col5 = st.columns(3)
col3.metric("Ano Atual", f"R$ {atual:,.2f}")
col4.metric("Ano Anterior", f"R$ {anterior:,.2f}")
col5.metric("Variação (%)", f"{variacao:.2f}%", delta=f"{variacao:.2f}%")

st.markdown("---")

# =========================
# 🎯 META vs REALIZADO
# =========================
meta_anual = 5_000_000  # Defina sua meta anual
dias_do_ano = 365
dias_corridos = (pd.to_datetime(data_fim) - pd.to_datetime(f"{data_fim.year}-01-01")).days + 1
meta_ate_hoje = (meta_anual / dias_do_ano) * dias_corridos
realizado = df_filtrado['Valor Líquido (R$)'].sum()
gap_percentual = ((realizado - meta_ate_hoje) / meta_ate_hoje) * 100

st.subheader("🎯 Meta vs Realizado")
col6, col7, col8 = st.columns(3)
col6.metric("Meta até hoje", f"R$ {meta_ate_hoje:,.2f}")
col7.metric("Realizado", f"R$ {realizado:,.2f}")
col8.metric("GAP", f"{gap_percentual:.2f}%", delta=f"{gap_percentual:.2f}%")

st.markdown("---")

# =========================
# 📅 GRÁFICO DE VENDAS MENSAIS
# =========================
df_filtrado['AnoMes'] = df_filtrado['Data Venda'].dt.to_period('M').astype(str)
graf_vendas = df_filtrado.groupby('AnoMes').sum(numeric_only=True).reset_index()
fig = px.bar(graf_vendas, x='AnoMes', y='Valor Líquido (R$)', title='📈 Evolução de Vendas Mensais')
st.plotly_chart(fig, use_container_width=True)

# =========================
# 🏆 RANKING DE VENDEDORES
# =========================
st.subheader("🏆 Ranking de Vendedores (Faturamento Líquido)")

ranking_vendedores = df_filtrado.groupby('Responsável Comercial')['Valor Líquido (R$)'].sum().reset_index()
ranking_vendedores = ranking_vendedores.sort_values(by='Valor Líquido (R$)', ascending=False)

fig_vendedores = px.bar(
    ranking_vendedores,
    x='Responsável Comercial',
    y='Valor Líquido (R$)',
    title='Top Vendedores',
    text_auto='.2s'
)

fig_vendedores.update_layout(xaxis_title="Vendedor", yaxis_title="Faturamento (R$)")
st.plotly_chart(fig_vendedores, use_container_width=True)

st.markdown("---")

# =========================
# 📄 DETALHAMENTO
# =========================
st.subheader("📄 Detalhamento das Vendas")
st.dataframe(df_filtrado)

st.caption("Dashboard com comparativos e ranking - Desenvolvido por Gabriel Leite Moreira 🚀")
