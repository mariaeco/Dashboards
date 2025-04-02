# streamlit run licitacoesPB.py #para rodar
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px

# with open('style.css') as f:
#     st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#VER ESSE SITE
#https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/

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
    df['month'] =df["DataCriacao1"].dt.strftime('%B') 
    df['year'] = df["DataCriacao1"].dt.year.astype(str)
    df['year_month'] = df["DataCriacao1"].dt.to_period("M").astype(str)
    df['ValorReal'] = df['Valor']
    df = df.drop(columns=['DataCriacao1'])
    return df

df = load_data()

print(df['month'])

#====================================== MAINPAGE ===========================================
st.title(":bar_chart: Dispensas de Licitação no Estado da Paraíba")
# st.markdown("##")

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



left_column, middle_columnt , right_column = st.columns([1,1,2])
with left_column:
    st.markdown(f'### Valor total licitado')
    st.markdown(f"**{valor_total}**")
with middle_columnt:
    st.markdown(f'### Número de Licitações') 
    st.markdown(f'**{n_total}**')
with right_column:
    st.markdown(f'### Licitação de maior valor') 
    st.markdown(f'**{lic_max}**')
    st.markdown(f'**Data:** {mes_lic_max}/{ano_lic_max}')
    st.markdown(f'**Órgão:** {orgao_max}')
    st.markdown(f'**Objeto:** {objeto_max}')



st.markdown("---")

#PRIMEIRO VOU FAZER ABAIXO OS PLOTS NÃO FILTRADOS (OU SEJA COM TODOS OS DADOS)
#DEPOIS VOU FAZER OS QUE LEVAM OS FILTROS EM CONSIDERAÇÃO

#====================================== 2 primeiros PLOTS ===========================================

list_year = (
    df.groupby(by=["year"])
    .sum()[['Valor']]
    .sort_values(by="year", ascending=True)
)

fig_list_year = px.bar(
    list_year, 
    y='Valor', 
    x=list_year.index,
    orientation='v',
    title="<b>Valor total licitado por ano <b>",
    labels={'Valor':'Valor (R$)', 'year':'Ano'},
    template='plotly_white',
    color=list_year["Valor"].apply(lambda x: np.log1p(x)), 
    color_continuous_scale='Blues',    
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
    template='plotly_white',
    color_discrete_sequence=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0", "#ffb3e6"]
)

fig_list_year.update_layout(
    height=300)
fig_max_year.update_layout(height=300)

#plotando os dois graficos   
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_list_year, use_container_width=True)
right_column.plotly_chart(fig_max_year, use_container_width=True)


#====================================== TERCEIRO E QUARTO PLOTS ===========================================
list_year_months = df.groupby(by=["year_month"]).sum()[['Valor']].reset_index()

fig_year_months = px.line(
    list_year_months, 
    x='year_month', 
    y='Valor',
    title="<b>Série temporal do valor licitado<b>",
    markers=True,  # Adiciona pontos nos dados
    line_shape='spline',  # Deixa a linha suave
    template='plotly_white',
    labels={'Valor': 'Valor (R$)', 'year_month': 'Ano-Mês'},
    color_discrete_sequence = ["#346beb"] 
)


left_column, right_column = st.columns(2)
with left_column:
    st.plotly_chart(fig_year_months, use_container_width=True)
    
# Filtrando o DataFrame pelo ano selecionado
with right_column:
    year_selected = st.selectbox(
        "Selecione o Ano:", 
        options=df['year'].unique(),
        index=0
    )
    df_filtered = df[df['year'] == year_selected]

    list_year = (
        df_filtered.groupby(by=["month"])["Valor"]
        .sum()
        .reset_index()  # Isso garante que "month" ainda é uma coluna
        
    )

    ordem_meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    list_year["month"] = pd.Categorical(list_year["month"], categories=ordem_meses, ordered=True)
    list_year = list_year.sort_values("month")


    # Criar o gráfico
    fig_year = px.bar(
        list_year, 
        x="month",
        y='Valor',
        title="<b>Valor Total Licitado por Mês/Ano<b>",
        template='plotly_white',
        labels={'Valor': 'Valor (R$)', 'year_month': 'Ano-Mês'},
        color=list_year["Valor"].apply(lambda x: np.log1p(x)), 
        color_continuous_scale="Blues",  # Aplicamos as cores personalizadas
    )

    fig_year.update_layout(height=350, xaxis=dict(tickangle=-45))
    st.plotly_chart(fig_year, use_container_width=True)



#====================================== quinto plot ===========================================

#lista de orgaos

list_orgaos = (
    df.groupby(by=["Orgao2"])
    .sum()[['Valor']]
    .sort_values(by="Valor", ascending=False)
)

top_orgaos = list_orgaos.head(10)

fig_list_orgaos = px.bar(
    top_orgaos, 
    x='Valor', 
    y=top_orgaos.index,
    orientation='h',
    title="<b>Valor total licitado por Órgão<b>",
    color='Valor',  # A cor será determinada pelo valor
    color_continuous_scale='Blues',
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white'
    )
fig_list_orgaos.update_layout(height=400)
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
    df_entity = df[df['Orgao2'] == entity]  # Filtra os dados do órgão selecionado
    objeto = st.selectbox(
        "Selecione o Objeto:", 
        options = df_entity['Objeto'].unique(),
        index=15
    )

# Filtrando o DataFrame com base no órgão selecionado---------------------------------------


# Filtrando o DataFrame com base no órgão e objeto selecionado
df_entity_objeto = df[(df['Orgao2'] == entity) & (df_entity['Objeto'] == objeto)]  # Filtra o órgão e o objeto


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

titulo_grafico = f"<b>Valor por Secretaria:\n {entity}</b>"
fig_list_year = px.bar(
    list_year, 
    y='Valor', 
    x=list_year.index,
    orientation='v',
    title= titulo_grafico,
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white',
    color='Valor',  # A cor será determinada pelo valor
    color_continuous_scale='Blues'
    )

#valor por ano/objeto da secretaria
list_year_objeto = (
    df_entity_objeto.groupby(by=["year"])
    .sum()[['Valor']]
    .sort_values(by="Valor", ascending=True)
)


titulo_grafico = f"<b>Valor por Objeto:\n {objeto}</b>"
fig_year_objeto = px.bar(
    list_year_objeto, 
    y='Valor', 
    x=list_year_objeto.index,
    orientation='v',
    title= titulo_grafico,
    color_discrete_sequence=['#346beb']*len(list_year_objeto),
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white',
    color='Valor',  # A cor será determinada pelo valor
    color_continuous_scale='Blues'
    )

with col2:
    st.plotly_chart(fig_list_year)

with col3:
    st.plotly_chart(fig_year_objeto)
    
# FILTRANDO OS OBJETOS ---------------------------------------------------------------------

#filtro de seleção da secretaria (plot do anual por secretaria - Secretaria como filtro)

st.markdown("---")
st.markdown("### OBJETOS")
objeto = st.selectbox(
    "Selecione o Órgão:", 
    options = df['Objeto'].unique(),
    index=6    
    )

df_objeto = df[(df['Objeto'] == objeto)]
                      
valor_total = df_objeto['Valor'].sum()
valor_total = locale.currency(valor_total, grouping=True)
st.write(f"Valor total licitado filtrado por objeto da Secretaria: **{valor_total}**")

#valor por ano da secretatia selecionada
list_objetos = (
    df_objeto.groupby(by=["year"])
    .sum()[['Valor']]
    .sort_values(by="Valor", ascending=True)
)

titulo_grafico = f"<b>Valor por Objeto:\n {objeto}</b>"
fig_list_objeto = px.bar(
    list_objetos, 
    y='Valor', 
    x=list_objetos.index,
    orientation='v',
    title= titulo_grafico,
    labels={'Valor':'Valor (R$)', 'Orgao2':'Órgão'},
    template='plotly_white',
    color='Valor',  # A cor será determinada pelo valor
    color_continuous_scale='Blues'
    )
st.plotly_chart(fig_list_objeto)