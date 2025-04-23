#streamlit run dashboard_licPB.py 
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from babel.numbers import format_currency
from plot_functions import plot_barh, donut, line_chart, barh_invertido, create_stats_table

pio.templates.default = None

st.set_page_config(page_title="Dispensas de Licitação", 
                   layout="wide", 
                   page_icon=":chart_with_downwards_trend:",
                   initial_sidebar_state="expanded")

#configurações de estilo
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            text-align: center;
        }
        .element-container {
            margin-bottom: 0.0rem;
            text-align: center; 
        }
        .stApp {
            background: linear-gradient(
                180deg,
                rgb(60, 95, 125) 0%,
                rgb(30, 47, 91) 100%
            ) !important;
        }
        section[data-testid="stSidebar"] {
            background: rgba(30, 47, 91, 0.5);
            color: white !important;
        }
            
        section[data-testid="stSidebar"] h1 {
            color: white !important; /* Força o título do sidebar a ser branco */
        }
        section[data-testid="stSidebar"] p {
            color: white !important;
        }
            
        header[data-testid="stHeader"] {
            background: transparent !important;
            backdrop-filter: blur(0px);
        }
        div[data-testid="stToolbar"] {
            background: transparent !important;
        }
        div[data-testid="stDecoration"] {
            background: transparent !important;
        }
            
        /* -------------- INFO-BOX ------------------------------*/
        .info-box {
            font-size: 1.5rem;
            text-align: center;
            color: white !important;
            background-color: #00162c;
            border-radius: 5px;
            margin-bottom: -40 !important;
            padding: 15px;
        }
            
        .stMetricValue {
            color: white !important; /* Força o texto das métricas a ser branco */
        }
            
        div[data-testid="stMetricValue"] {
            color: white !important;
        }
            
        div[data-testid="stNotificationContentInfo"] {
            color: white !important;
        }
        /* ------------- TITULO DOS GRAFICOS -----------------*/

        div.titulo-container {
            background-color: #00162c;
            margin-bottom: 0px;
            padding: 0px;
            text-align: center;
            border-radius: 10px 10px 0px 0px;
        }
        
        /* Estilo para o título */
        div.titulo-container h4 {
            margin: 0;
            padding: 15px;
            color: white;
            font-size: 16px;
        }
        
        /* Remove margens do plotly */
        .js-plotly-plot {
            margin-top: -10px;
        }
        .js-plotly-plot .plot-container {
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
            overflow: hidden;
            color: white !important;
        }
        

        /* ---------------- TABELA -------------------------*/
        div[data-testid="stTable"] {
            width: 100% !important;
            background-color: #1c2637 !important;
            color: white !important;
            font-size: 14px !important;
            border: none !important;
            border-collapse: collapse !important;
            border-radius: 0px 0px 10px 10px !important; /* Bordas arredondadas na parte inferior */
            overflow: hidden !important;
        }

        /* Estilo específico para título da tabela */
        div.titulo-tabela {
            background-color: #00162c;
            margin-bottom: -25px;
            padding: 0px;
            text-align: center;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        
        div.titulo-tabela h4 {
            margin: 0;
            padding: 15px;
            color: white !important;
            font-size: 16px;
        }
        table {
            width: 100%;
            border: none;
        }
            
        thead th {
            background-color: #00162c;
            color: white !important; /* Cor do texto do cabeçalho */
        }
        tbody tr:nth-child(odd) {
            background-color: #f9f9f9;
        }
        tbody tr:nth-child(even) {
            background-color: #e0e0e0;
        }
        tbody td {
            color: #333333; /* Cor do texto das células */}
        }
            
  


    </style>
""", unsafe_allow_html=True)


# st.title(":chart_with_downwards_trend: Dispensas de Licitação - PB")
# st.markdown("Análise de dados de dispensa de licitação do Governo da Paraíba entre os anos de 2019 e 2024. _**Fonte:** Portal da Transparência do Governo da Paraíba_")


# Carregar os dados
@st.cache_data #decorator - armazena em cache para não precisar carregar toda vez que atualizar a página
def load_data():
    file_path = "df_padronizado.csv"
    df = pd.read_csv(file_path, header=0, sep=',', encoding="latin1")
    df["StartDate"] = pd.to_datetime(df["Data de Abertura"], format="%d/%m/%Y")
    df['month'] =df["StartDate"].dt.strftime('%b') 
    df['Ano'] = df["StartDate"].dt.year.astype(str)
    df['year_month'] = df["StartDate"].dt.to_period("M").astype(str)
    
    df = df.rename(columns={"Valor_transformado": "Value", "CagGasto": "Categoria", "Siglas": "Secretaria", 
                            "ClasseObj": "Objetos", "ValorReal": "Value", "Razão Social": "Contratado"})
    
    # Extrair apenas o nome da empresa da coluna "Contratado"
    df['EmpresaContratada'] = df['Contratado'].str.split(' - ', n=1).str[1]
    
    df = df.drop(columns=['Data de Abertura'])
    return df

df = load_data()
# ================ SIDEBAR E FILTROS =====================================================================

selected_orgao = 'Todos as Secretarias'
selected_obj = 'Todos os Objetos'
selected_empresa = 'Todas as Empresas'

with st.sidebar:
    st.title(':pencil: Dispensas de Licitação - PB (2019-2024)')
    
    # Seletor de ano
    year_list = list(df.Ano.unique())[::-1]
    selected_year = st.selectbox('Selecione um ano', ['Todos os Anos'] + year_list, index=0)
    if selected_year != 'Todos os Anos':
        df_year = df[df['Ano'] == selected_year]
        df_filtered = df[df['Ano'] == selected_year]
    else:
        df_year = df
        df_filtered = df
    
    # Seletor de variável (Secretaria ou Objetos)

    # Seletor DA SECRETARIA
    ordem_desejada = [
        'SES', 'SEE', 'SEDH', 'PMPB', 'CBMPB', 'SEC', 'SEINFRA', 'PROJETO COOPERAR',
        'SER', 'EGE', 'SEIE', 'SEAD', 'SECOM', 'CCG', 'SIE',
        'SEPLAN', 'SEDAP', 'DETRAN', 'SEDS', 'SEFAZ', 'SECTMA',
        'SEAP', 'SETDE', 'CASA MILITAR', 'SEAFD', 'SESDS',
        'PROJETO CARIRI', 'POLICIA CIVIL', 'IPEP', 'FEPDC', 'SEJEL', 'PGE', 'SEMDH',
        'SEG', 'SEDAM'
    ]
    orgao_list = [sec for sec in ordem_desejada if sec in df.Secretaria.unique()]
    orgao_list = ['Todos as Secretarias'] + orgao_list
    selected_orgao = st.selectbox('Selecione uma Secretaria', orgao_list, index=0)
    if selected_orgao != 'Todos as Secretarias':
        df_filtered = df_filtered[df_filtered['Secretaria'] == selected_orgao]
    
    
    var_list = ['Objetos', 'Contratados']
    selected_var = st.selectbox('Selecione uma variável', var_list, index=0)
    if selected_var == 'Contratados':
        empresa_list = list(df.EmpresaContratada.unique())
        empresa_list = ['Todas as Empresas'] + empresa_list
        selected_empresa = st.selectbox('Selecione uma Empresa', empresa_list, index=0)
        if selected_empresa != 'Todas as Empresas':
            df_filtered = df_filtered[df_filtered['EmpresaContratada'] == selected_empresa]
    elif selected_var == 'Objetos':
        obj_list = list(df.Objetos.unique())
        obj_list = ['Todos os Objetos'] + obj_list
        selected_obj = st.selectbox('Selecione um Objeto', obj_list, index=0)
        if selected_obj != 'Todos os Objetos':
            df_filtered = df_filtered[df_filtered['Objetos'] == selected_obj]



# =================================================================================================================================================================
# ============ DEFINING STRUCTURE =================================================================================================================================
# =================================================================================================================================================================

# TOP METRICS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
col = st.columns((1, 1, 1), gap='medium')
col1, col2, col3 = col[0], col[1], col[2]


# Filtra os dados com base no ano e na secretaria selecionados para as métricas
df_filtered_metrics = df
if selected_year != 'Todos os Anos':
    df_filtered_metrics = df_filtered_metrics[df_filtered_metrics['Ano'] == selected_year]

if selected_orgao != 'Todos as Secretarias':
    df_filtered_metrics = df_filtered_metrics[df_filtered_metrics['Secretaria'] == selected_orgao]
elif selected_var == 'Objetos':
    if selected_obj != 'Todos os Objetos':
        df_filtered_metrics = df_filtered_metrics[df_filtered_metrics['Objetos'] == selected_obj]
elif selected_var == 'Contratados':
    if selected_empresa != 'Todas as Empresas':
        df_filtered_metrics = df_filtered_metrics[df_filtered_metrics['EmpresaContratada'] == selected_empresa]


# Calcula as métricas com base nos filtros
valor_total = df_filtered_metrics['Value'].sum()
n_total = len(df_filtered_metrics)  # Conta o número total de registros
lic_max = df_filtered_metrics['Value'].max() if not df_filtered_metrics.empty else 0


# Cálculo do delta (comparação com ano anterior)
delta = None
delta_text = None
if selected_year != 'Todos os Anos' and selected_year != '2019':
    ano_anterior = str(int(selected_year) - 1)
    valor_anterior = df[(df['Ano'] == ano_anterior) & (df['Secretaria'] == selected_orgao)]['Value'].sum()
    delta = valor_total - valor_anterior
    delta_text = format_currency(abs(delta), 'BRL', locale='pt_BR')
    delta_text = f"-{delta_text}" if delta < 0 else f"+{delta_text}"


valor_total = format_currency(valor_total, 'BRL', locale='pt_BR')
lic_max = format_currency(lic_max, 'BRL', locale='pt_BR')


with col1:
    st.markdown("<div class='info-box'>Valor Total de Dispensas</div>", unsafe_allow_html=True)
    st.metric(label="", value=valor_total) #, delta=delta_text

with col2:
    st.markdown("<div class='info-box'>Total de Dispensas</div>", unsafe_allow_html=True)
    st.metric(label="", value=n_total)

with col3:
    st.markdown("<div class='info-box'>Maior Licitação</div>", unsafe_allow_html=True)
    st.metric(label="", value=lic_max)


st.markdown("""
    <hr style="height:2px;
              border-width:0;
              color:#7BA3CC;
              background-color:#7BA3CC;
              margin-top: 0;
              margin-bottom: 0;">
""", unsafe_allow_html=True)




# ============ GRAFICOS =================================================================================================================================

# ---------- ESTRUTURA DOS GRAFICOS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#2 COLUNAS EM CIMA (BARPPLOT-HORIZONTAL ADJUDICADO POR SECRETARIA, ACHO QUE A TABELA COMVALORES DE OBJETO POR SECRETARIA)
linha1g1, linha1g2 = st.columns((1, 1), gap='medium')


#3 COLUNAS EM BAIXO (BARPLOT - ADJUDICADO POR ANO, DONUT-CHART:QTD DE AJDUJUDICADOS ABAIXO DE 50MIL E ACIMA DE 150MIL)
linha2g1, linha2g2, linha2g3= st.columns((1, 1.5, 1.5), gap='medium')



# =================================================================================================================================================================
# ============ GRAFICOS =================================================================================================================================

with linha1g1:
    st.markdown(
        """
        <div class="titulo-container">
            <h4>Dispensas por Categoria</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    fig = plot_barh(df_year)
    st.plotly_chart(fig, use_container_width=True)

with linha1g2:
    st.markdown(
        """
        <div class="titulo-tabela">
            <h4>Estatísticas</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    stats_table = create_stats_table(df_filtered)
    st.table(stats_table)    


with linha2g1:
    fig = donut(df_filtered,selected_year)
    st.plotly_chart(fig, use_container_width=True)


with linha2g2:
    fig = line_chart(df_filtered,selected_year)
    st.plotly_chart(fig, use_container_width=True)


with linha2g3:
    if selected_var == 'Contratados':
        fig = barh_invertido(df_year[df_year['Secretaria'] == selected_orgao] if selected_orgao != 'Todos as Secretarias' else df_year, 'EmpresaContratada')
    elif selected_var == 'Objetos':
        fig = barh_invertido(df_year[df_year['Secretaria'] == selected_orgao] if selected_orgao != 'Todos as Secretarias' else df_year, 'Objetos')
    st.plotly_chart(fig, use_container_width=True)
