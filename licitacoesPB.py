# streamlit run licitacoesPB.py #para rodar
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px

# from scipy.interpolate import make_interp_spline, BSpline

import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

st.set_page_config(page_title="Dispensas de Licitação", 
                   layout="wide", 
                   page_icon="📊")


# Carregar os dados
@st.cache_data #decorator - armazena em cache para não precisar carregar toda vez que atualizar a página
def load_data():
    file_path = "dislit_final.csv"
    df = pd.read_csv(file_path, header=0, sep=',')
    df["DataCriacao1"] = pd.to_datetime(df["DataCriacao1"], format="%d/%m/%Y")
    df['month'] =df["DataCriacao1"].dt.strftime('%b') 
    df['year'] = df["DataCriacao1"].dt.year.astype(str)
    df['year_month'] = df["DataCriacao1"].dt.to_period("M").astype(str)
    df['ValorReal'] = df['Valor']
    df = df.drop(columns=['DataCriacao1'])
    return df

df = load_data()


#====================================== MAINPAGE ===========================================
st.title(":bar_chart: Dispensas de Licitação no Estado da Paraíba")
st.markdown("##")

#top results
valor_total = df['Valor'].sum()
valor_total = locale.currency(valor_total, grouping=True)
n_total = df['Textbox2'].count()
lic_max= df['Valor'].max()
ano_lic_max = df.loc[df['Valor'] == lic_max, 'year'].iloc[0]
mes_lic_max = df.loc[df['Valor'] == lic_max, 'month'].iloc[0]
orgao_max = df.loc[df['Valor'] == lic_max, 'Orgao2'].iloc[0]
objeto_max = df.loc[df['Valor'] == lic_max, 'Objeto'].iloc[0]
lic_max = locale.currency(lic_max, grouping=True)


left_column, middle_columnt , right_column = st.columns(3)
with left_column:
    st.markdown("### Valor total licitado")
    st.markdown(f"**{valor_total}**")
with middle_columnt:
    st.markdown("### Número de Licitações") 
    st.markdown(f"**{n_total}**")
with right_column:
    st.markdown("### Licitação de maior valor") 
    st.markdown(f"**{lic_max}**")
    st.markdown(f"**Data:** {mes_lic_max}/{ano_lic_max}")
    st.markdown(f"**Órgão:** {orgao_max}")
    st.markdown(f"**Objeto:** {objeto_max}")



st.markdown("---")

#PRIMEIRO VOU FAZER ABAIXO OS PLOTS NÃO FILTRADOS (OU SEJA COM TODOS OS DADOS)
#DEPOIS VOU FAZER OS QUE LEVAM OS FILTROS EM CONSIDERAÇÃO

#====================================== 2 primeiros PLOTS ===========================================
list_year = (
    df.groupby(by=["year"])
    .sum()[['Valor']]
    .sort_values(by="year", ascending=False)
)

fig_list_year = px.bar(
    list_year, 
    x='Valor', 
    y=list_year.index,
    orientation='h',
    title="<b>Valor total licitado por ano <b>",
    color_discrete_sequence=['#346beb']*len(list_year),
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white'
    )

#Maiores valores de cada ano
maiores_por_ano = df.groupby('year').agg({'Valor': 'max'}).reset_index()
orgaos_max = []
for ano in maiores_por_ano['year']:
    orgao_max = df[(df['year'] == ano) & (df['Valor'] == df[df['year'] == ano]['Valor'].max())]['Orgao2'].iloc[0]
    orgaos_max.append(orgao_max)

maiores_por_ano['Orgao'] = orgaos_max
maiores_por_ano['Valor_formatado'] = maiores_por_ano['Valor'].apply(lambda x: locale.currency(x, grouping=True))

fig_max_year = px.pie(
    maiores_por_ano, 
    names='year',  # Categorias serão os anos
    values='Valor',  # Medida das fatias será o valor licitado
    title="<b>Distribuição do Maior Valor Licitado por Ano</b>",
    hover_data={'Orgao': True},  # Mostrar detalhes ao passar o mouse
    template='plotly_white'
)

#plotando os dois graficos   
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_list_year, use_container_width=True)
right_column.plotly_chart(fig_max_year, use_container_width=True)


#====================================== TERCEIRO E QUURTA PLOTS ===========================================
list_year_months = df.groupby(by=["year_month"]).sum()[['Valor']].reset_index()

fig_year_months = px.line(
    list_year_months, 
    x='year_month', 
    y='Valor',
    title="<b>Valor Total Licitado por Mês<b>",
    markers=True,  # Adiciona pontos nos dados
    line_shape='spline',  # Deixa a linha suave
    template='plotly_white',
    labels={'Valor': 'Valor (R$)', 'year_month': 'Ano-Mês'}
)
st.plotly_chart(fig_year_months)




list_orgaos = (
    df.groupby(by=["Orgao2"])
    .sum()[['Valor']]
    .sort_values(by="Valor", ascending=False)
)

fig_list_orgaos = px.bar(
    list_orgaos, 
    x='Valor', 
    y=list_orgaos.index,
    orientation='h',
    title="<b>Valor total licitado por Órgão<b>",
    color_discrete_sequence=['#346beb']*len(list_orgaos),
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white'
    )

st.plotly_chart(fig_list_orgaos)







#====================================== FILTROS =====================================================

#====================================  SIDEBAR  =====================================================
st.markdown("---")

#filtro de seleção da secretaria (plot do anual por secretaria - Secretaria como filtro)
col1, col2, col3 = st.columns([1, 2, 3])  

with col1:
    st.markdown("### SECRETARIAS")
    entity = st.selectbox(
        "Selecione o Órgão:", 
        options = df['Orgao2'].unique(),
        index=4       
        )
    
    objeto = st.selectbox(
        "Selecione o Objeto:", 
        options = df['Objeto'].unique(),
        index=15
    )

df_entity = df.query("Orgao2 == @entity") #para poder aplicar o filtro tenho que definir aqui a variavel e seu filtro
df_entity_objeto = df.query("Orgao2 == @entity and Objeto == @objeto") #para poder aplicar o filtro tenho que definir aqui a variavel e seu filtro


valor_total = df_entity['Valor'].sum()
valor_total = locale.currency(valor_total, grouping=True)
st.write(f"Valor total licitado filtrado por Secretaria: **{valor_total}**")


valor_total = df_entity_objeto['Valor'].sum()
valor_total = locale.currency(valor_total, grouping=True)
st.write(f"Valor total licitado filtrado por objeto: **{valor_total}**")

#valor por ano da secretatia selecionada
list_year = (
    df_entity.groupby(by=["year"])
    .sum()[['Valor']]
    .sort_values(by="year", ascending=True)
)

titulo_grafico = f"<b>Valor por Secretaria: {entity}</b>"
fig_list_year = px.bar(
    list_year, 
    y='Valor', 
    x=list_year.index,
    orientation='v',
    title= titulo_grafico,
    color_discrete_sequence=['#346beb']*len(list_year),
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white'
    )

#valor por ano/objeto da secretaria
list_year_objeto = (
    df_entity_objeto.groupby(by=["year"])
    .sum()[['Valor']]
    .sort_values(by="year", ascending=True)
)

titulo_grafico = f"<b>Valor por Objeto: {objeto}</b>"
fig_year_objeto = px.bar(
    list_year_objeto, 
    y='Valor', 
    x=list_year_objeto.index,
    orientation='v',
    title= titulo_grafico,
    color_discrete_sequence=['#346beb']*len(list_year_objeto),
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white'
    )

with col2:
    st.plotly_chart(fig_list_year)

with col3:
    st.plotly_chart(fig_year_objeto)
    




# ----------------------------------------------------------------------
#f Filtro por ano: secretarias com mais gastos por ano
# Criando duas colunas
col1, col2 = st.columns([1, 3])  

with col1:
    st.markdown("### Secretarias por ano")
    year_selected = st.selectbox(
        "Selecione o Ano:", 
        options=df['year'].unique(),
        index=0
    )

# Filtrando o DataFrame pelo ano selecionado
df_filtered = df[df['year'] == year_selected]

# Agrupando os valores por Secretaria e ordenando do maior para o menor
list_orgaos = (
    df_filtered.groupby(by=["Orgao2"])
    .sum()[['Valor']]
    .sort_values(by="Valor", ascending=False)
)

# Criando o gráfico
fig_list_orgaos = px.bar(
    list_orgaos, 
    x='Valor', 
    y=list_orgaos.index,
    orientation='h',
    title=f"<b>Secretarias com Maior Gasto em {year_selected}</b>",
    color_discrete_sequence=['#346beb'] * len(list_orgaos),
    labels={'Valor': 'Valor (R$)', 'Orgao2': 'Órgão'},
    template='plotly_white'
)

# Exibindo o gráfico na segunda coluna
with col2:
    st.plotly_chart(fig_list_orgaos)

