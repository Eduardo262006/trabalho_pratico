import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard Portugal (2000 - 2023)", layout="wide")

@st.cache_data
def load_data():
    conn = duckdb.connect("data/database/analytical_warehouse.duckdb")
    df = conn.execute("SELECT * FROM gold_metrics_pt ORDER BY Ano").df()
    conn.close()
    return df

df = load_data()

st.sidebar.subheader("Filtro Temporal")
anos_lista = sorted(df['Ano'].unique().tolist())

year_range = st.sidebar.select_slider(
    "Selecione o período:",
    options=anos_lista,
    value=(anos_lista[0], anos_lista[-1])
)

df_filt = df[(df['Ano'] >= year_range[0]) & (df['Ano'] <= year_range[1])]

st.title("Monitorização Socioeconómica e Climática")
st.markdown(f"**Portugal ({year_range[0]} - {year_range[1]})** | Análise de indicadores da Camada Gold.")

tab_econ, tab_clim, tab_soc, tab_corr = st.tabs(["💰 Economia", "🌿 Ambiente", "📱 Social & Digital", "📊 Correlações"])

with tab_econ:
    col1, col2, col3 = st.columns(3)
    ult_ano = df_filt.iloc[-1]
    ant_ano = df_filt.iloc[0]
    
    col1.metric("PIB per Capita", f"${ult_ano['PIB_per_capita']:,.0f}", f"{ult_ano['PIB_per_capita'] - ant_ano['PIB_per_capita']:+.0f}")
    col2.metric("Inflação Anual", f"{ult_ano['Inflação(% anual)']:.2f}%", f"{ult_ano['Inflação(% anual)'] - ant_ano['Inflação(% anual)']:+.2f}")
    col3.metric("Desemprego", f"{ult_ano['Desemprego(% trabalhadores)']:.2f}%", f"{ult_ano['Desemprego(% trabalhadores)'] - ant_ano['Desemprego(% trabalhadores)']:+.2f}")

    fig_econ = make_subplots(specs=[[{"secondary_y": True}]])
    fig_econ.add_trace(go.Bar(x=df_filt['Ano'], y=df_filt['PIB_per_capita'], name="PIB per capita ($)", marker_color='#2c3e50', opacity=0.8), secondary_y=False)
    fig_econ.add_trace(go.Scatter(x=df_filt['Ano'], y=df_filt['Investimento_Estrangeiro'], name="Investimento Estrangeiro (%)", mode='lines+markers', line=dict(color='#e74c3c', width=3)), secondary_y=True)
    
    fig_econ.update_layout(title="Relação entre Crescimento do PIB e Investimento Estrangeiro", hovermode="x unified", height=450)
    fig_econ.update_yaxes(title_text="PIB per capita (USD)", secondary_y=False)
    fig_econ.update_yaxes(title_text="Investimento Estrangeiro (%)", secondary_y=True)
    st.plotly_chart(fig_econ, use_container_width=True)

with tab_clim:
    fig_temp = px.line(df_filt, x="Ano", y=["T2M_Media_Anual", "T2M_Maxima_Anual", "T2M_Minima_Anual"],
                       title="Tendências Térmicas Anuais (NASA POWER)",
                       labels={"value": "Temperatura ºC", "variable": "Métrica"},
                       color_discrete_sequence=['#f39c12', '#e74c3c', '#3498db'])
    st.plotly_chart(fig_temp, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        fig_en = px.area(df_filt, x="Ano", y="Producao_de_Energia_Renovavel(% do total)", title="Produção de Energia Renovável (%)", color_discrete_sequence=['#2ecc71'])
        st.plotly_chart(fig_en, use_container_width=True)
    with c2:
        fig_co2 = px.scatter(df_filt, x="Ano", y="CO2_per_capita", size="Populacao", color="CO2_per_capita", title="Emissões de CO2 per capita", color_continuous_scale="Reds")
        st.plotly_chart(fig_co2, use_container_width=True)

with tab_soc:
    fig_soc = px.scatter(df_filt, x="Utilizadores_de_Internet(% populacao)", y="Esperança_de_Vida", 
                         size="Gastos_com_Educacao(% PIB)", color="Ano",
                         title="Digitalização vs Longevidade (Tamanho da bolha = Gastos com Educação)",
                         color_continuous_scale="Tealgrn")
    st.plotly_chart(fig_soc, use_container_width=True)

with tab_corr:
    st.markdown("### Matriz de Correlação de Indicadores")
    st.info("Descobre como as variáveis climáticas e económicas se influenciam mutuamente.")
    cols_corr = ["PIB_per_capita", "Esperança_de_Vida", "Amplitude_Termica", "Utilizadores_de_Internet(% populacao)", "Desemprego(% trabalhadores)", "CO2_per_capita", "Inflação(% anual)"]
    corr = df_filt[cols_corr].corr()
    fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r', aspect="auto")
    fig_corr.update_layout(height=600)
    st.plotly_chart(fig_corr, use_container_width=True)