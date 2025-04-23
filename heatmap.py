#streamlit run heatmap.py 
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

## STREAMLIT EMOJIS: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

st.set_page_config(page_title="Dispensas de Licitação", 
                   layout="wide", 
                   page_icon=":chart_with_downwards_trend:",
                   initial_sidebar_state="expanded")
alt.themes.enable("dark")

st.title(":chart_with_downwards_trend: Dispensas de Licitação - PB")
st.markdown("Análise de dados de dispensa de licitação do Governo da Paraíba entre os anos de 2019 e 2024. _**Fonte:** Portal da Transparência do Governo da Paraíba_")


# Carregar os dados
@st.cache_data #decorator - armazena em cache para não precisar carregar toda vez que atualizar a página
def load_data():
    file_path = "df_padronizado.csv"
    df = pd.read_csv(file_path, header=0, sep=',', encoding="latin1")
    df["StartDate"] = pd.to_datetime(df["Data de Abertura"], format="%d/%m/%Y")
    df['month'] =df["StartDate"].dt.strftime('%B') 
    df['year'] = df["StartDate"].dt.year.astype(str)
    df['year_month'] = df["StartDate"].dt.to_period("M").astype(str)
    
    df = df.rename(columns={"Valor_transformado": "Value", "CagGasto": "Categoria", "Siglas": "Secretaria", "ClasseObj": "Objetos", "ValorReal": "Value"})
    
    df = df.drop(columns=['Data de Abertura'])
    return df

df = load_data()
print(df.columns)
# ================ SIDEBAR E FILTROS =====================================================================


with st.sidebar:
    st.title(':pencil: Dashboard de Dispensas de Licitação - PB')
    
    var_list = list(['Objetos', 'Secretaria'])
    selected_var = st.selectbox('Selecione um objeto de licitação', var_list, index=len(var_list)-1)

    year_list = list(df.year.unique())[::-1]
    # selected_year = st.selectbox('Selecione um ano', year_list, index=len(year_list)-1)
    # df_selected_year = df[df.year == selected_year]
    # df_selected_year_sorted = df_selected_year.sort_values(by="Value", ascending=False)

    orgao_list = list(df.Secretaria.unique())[::-1]
    #selected_orgao = st.selectbox('Selecione um órgão', orgao_list, index=len(orgao_list)-1)
    # df_selected_orgao = df[df.Secretaria == selected_orgao]
    # df_selected_orgao_sorted = df_selected_orgao.sort_values(by="Value", ascending=False)

    obj_list = list(df.Categoria.unique())[::-1]
    #selected_obj = st.selectbox('Selecione um objeto de licitação', obj_list, index=len(obj_list)-1)
    # df_selected_obj = df[df.Categoria == selected_obj]
    # df_selected_obj_sorted = df_selected_obj.sort_values(by="Value", ascending=False)

    # color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    # selected_color_theme = st.selectbox('Select a color theme', color_theme_list)



# =================================================================================================================================================================
# ============ PLOT FUNCTIONS ====================================================================================================================
# =================================================================================================================================================================



#HEATMAP ================================================================================================================================	

def make_heatmap(input_df, input_y, input_x, input_value, input_color_theme, angle=0):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=angle)),
            color=alt.Color(f'max({input_value}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme, type='log')),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900, height=500
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    return heatmap


#BARHCHART ================================================================================================================================	
def make_chart(input_df, input_y, input_x, input_value):
# def survey(results, category_names):
#make_chart(count_year_categ, 'year', selected_var,'Value')

    labels = input_df[input_y]
    data = input_df[input_value]
    data_cum = data.cumsum(axis=1)
    category_colors = plt.colormaps['RdYlGn'](
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(input_df[input_x], category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, label_type='center', color=text_color)
    ax.legend(ncols=len(input_df[input_x]), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax


# =================================================================================================================================================================
# ============ DEFINING AND APPLYNG STRUCTURE TO DASHBOARD ====================================================================================================================
# =================================================================================================================================================================
col = st.columns((1.5, 4.5, 2), gap='medium')

# APPLYING HEATMATPS ================================================================================================================================
#CONTAGEM POR VARIAVEL - GARINTINDO QUE SE NÃO EXISTE DISPENSA PARA A SECRETARIA/OBJETO/CATEGORIA, O VALOR É ZERO
#Secretaria 
count_year_orgao = df.groupby(by=["year", "Secretaria"]).count()[['Value']]
all_combinations = pd.MultiIndex.from_product(
    [df['year'].unique(), df['Secretaria'].unique()], names=["year", "Secretaria"]
)
count_year_orgao = count_year_orgao.reindex(all_combinations, fill_value=0).reset_index()
count_year_orgao['Value'] = count_year_orgao['Value']+1 #adicionando para evitar log0

#Objeto
count_year_obj = df.groupby(by=["year", "Objetos"]).count()[['Value']]
all_combinations = pd.MultiIndex.from_product(
    [df['year'].unique(), df["Objetos"].unique()], names=["year", "Objetos"]
)
count_year_obj = count_year_obj.reindex(all_combinations, fill_value=0).reset_index()
count_year_obj['Value'] = count_year_obj['Value']+1 #adicionando para evitar log0

#Categoria de Gasto
count_year_categ = df.groupby(by=["year", "Categoria"]).count()[['Value']]
all_combinations = pd.MultiIndex.from_product(
    [df['year'].unique(), df['Categoria'].unique()], names=["year", "Categoria"]
)
count_year_categ = count_year_categ.reindex(all_combinations, fill_value=0).reset_index()
count_year_categ['Value'] = count_year_categ['Value']+1 #adicionando para evitar log0


with col[1]:
    if selected_var == 'Secretaria':
        heatmap = make_heatmap(count_year_orgao, 'year', selected_var, 'Value', 'reds', angle = -90)
        st.altair_chart(heatmap, use_container_width=True)
    elif selected_var == 'Objetos':   #<----------------------------------------------------- MUDAR ESSE GRAFIFCO PARA BARCHART
        heatmap = make_heatmap(count_year_obj, 'year', selected_var, 'Value', 'reds', angle = 45)
        st.altair_chart(heatmap, use_container_width=True)
    # elif selected_var == 'Categoria': #<----------------------------------------------------- MUDAR ESSE GRAFIFCO PARA BARCHART
    #     #barchart = make_chart(count_year_categ, 'year', selected_var,'Value')
    #     heatmap = make_heatmap(count_year_categ, 'year', selected_var, 'Value', 'reds')
    #     st.altair_chart(heatmap, use_container_width=True)
