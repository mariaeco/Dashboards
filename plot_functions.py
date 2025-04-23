import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from babel.numbers import format_currency

# ---------- FUNÇÕES DOS GRÁFICOS E TABELAS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def plot_barh(df):
    list_orgaos = (
        df.groupby('Secretaria')
        .agg({"Value": "sum"})
        .reset_index()
        .sort_values(by="Value", ascending=False)
    )

    top_orgaos = list_orgaos.head(8).sort_values(by="Value", ascending=True)
    top_orgaos['valor_formatado'] = top_orgaos['Value'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))

    fig = px.bar(
        top_orgaos,
        x='Value',
        y='Secretaria',
        orientation='h',
        color=top_orgaos["Value"].apply(lambda x: np.log1p(x)),
        color_continuous_scale='Blues',
        text='valor_formatado'
    )

    fig.update_traces(
        textposition='outside',
        textfont=dict(color="white", size=12),
        hovertemplate=None,
        hoverinfo='skip'
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        font=dict(color="white"),
        showlegend=False,
        height=238,
        width=100,
        margin=dict(l=10, r=10, t=15, b=10),
        plot_bgcolor='#34495e',
        paper_bgcolor='#34495e',
        coloraxis_showscale=False,
        xaxis=dict(
            range=[0, top_orgaos['Value'].max() * 1.2],
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)'
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)'
        )
    )

    return fig

def create_stats_table(df):
    stats_df = df.groupby('Ano').agg({
        'Value': ['max', 'mean', 'min']
    }).reset_index()
    stats_df.columns = ['Ano', 'Máximo', 'Média', 'Mínimo']
    for col in ['Máximo', 'Média', 'Mínimo']:
        stats_df[col] = stats_df[col].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    return stats_df

def donut(df, categoria):
    df['Categoria'] = pd.cut(df['Value'], bins=[0, 50000, 100000, 150000, float('inf')], 
                             labels=['<50 mil', '50-100 mil', '100-150 mil','>150 mil'])
    counts = df['Categoria'].value_counts().reset_index()
    counts.columns = ['Categoria', 'Contagem']

    fig = px.pie(counts, 
                 values='Contagem', 
                 names='Categoria', 
                 hole=0.7, 
                 color_discrete_sequence=['#001f3f', '#0074D9', '#7FDBFF', '#39CCCC'],
                 title='',
                 labels={'Contagem': 'Quantidade'})

    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=20, t=30, b=5),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        xaxis=dict(
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)'
        ),
        yaxis=dict(
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)'
        )
    )
    return fig

def line_chart(df, selected_year):
    if selected_year != 'Todos os Anos':
        df_plot = df[df['Ano'] == selected_year].groupby('month').agg({'Value': 'mean'}).reset_index()
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        df_plot['month'] = pd.Categorical(df_plot['month'], categories=month_order, ordered=True)
        df_plot = df_plot.sort_values('month')
        x_axis = 'month'
        title_text = f"{selected_year}"
    else:
        df_plot = df.groupby('Ano').agg({'Value': 'sum'}).reset_index()
        x_axis = 'Ano'
        title_text = "Soma Anual"

    fig = px.area(df_plot, x=x_axis, y='Value', markers=True)
    fig.update_traces(
        line=dict(color='#1f77b4', width=4),
        marker=dict(size=8, color='#ff7f0e')
    )
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.7,
            y=0.9,
            font=dict(size=14, color="white")
        ),
        xaxis_title=None,
        yaxis_title=None,
        font=dict(color="white"),
        showlegend=False,
        height=200,
        width=100,
        margin=dict(l=10, r=10, t=15, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickmode='linear',
            tickangle=-90,
            color='white',
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)'
        ),
        yaxis=dict(
            color="white",
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)'
        )
    )
    return fig

def barh_invertido(df, categoria):
    df_grouped = df.groupby([categoria]).agg({'Value': 'sum'}).reset_index()
    df_grouped = df_grouped.sort_values(by='Value', ascending=True).tail(5)
    df_grouped['Value'] = -df_grouped['Value']
    df_grouped['Valor Formatado'] = df_grouped['Value'].apply(lambda x: format_currency(abs(x), 'BRL', locale='pt_BR'))

    fig = px.bar(
        df_grouped,
        x='Value',
        y=categoria,
        orientation='h',
        text='Valor Formatado',
        color=categoria,
        color_discrete_sequence=['#DDDDDD', '#39CCCC', '#7FDBFF', '#0074D9', '#001f3f']
    )

    fig.update_traces(
        textposition='auto',
        textfont=dict(color="white", size=12),
        insidetextanchor='middle'
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        font=dict(color="white"),
        height=240,
        width=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False,
        xaxis=dict(
            tickformat=".2s",
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)',
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickvals=[-df_grouped['Value'].min(), 0],
            ticktext=[format_currency(abs(df_grouped['Value'].min()), 'BRL', locale='pt_BR'), "0"]
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='white'),
            zerolinecolor='rgba(255, 255, 255, 0.3)'
        )
    )
    return fig