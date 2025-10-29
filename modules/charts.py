import pandas as pd
import numpy as np
import inflection
import plotly.express as px
from typing import Optional
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

def agrupamento(df, *, agrupador: str, alvo: str, operacao: str, linhas=None):
    """
    Agrupa e ordena resultados por uma coluna específica.
    """
    idx = linhas if linhas is not None else slice(None)
    df_sel = df.loc[idx, [agrupador, alvo]]
    gb = df_sel.groupby(agrupador)[alvo]
    if not hasattr(gb, operacao):
        raise ValueError(f"Operação '{operacao}' inválida para GroupBy.")
    return getattr(gb, operacao)().reset_index(name=alvo)

def grafico_agrupamento(
    df,
    *,
    grafico: str,                     # 'bar' | 'line' | 'pie' | 'scatter'
    x: Optional[str] = None,
    y: Optional[str] = None,
    names: Optional[str] = None,
    values: Optional[str] = None,
    title: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,       # scatter pode usar tamanho de bolhas
    hover_name: Optional[str] = None, # scatter/pie
    orientation: str = 'v',
    text: Optional[str] = None,       # <- NOVO: coluna com os rótulos
    text_auto: bool = False           # <- NOVO: exibir texto automático
):
    g = grafico.lower()  
    # ----------------------------
    # Gráficos baseados em eixo XY
    # ----------------------------
    if g in ('bar', 'line', 'scatter'):
        if not x or not y:
            raise ValueError(f"Para '{g}', informe x e y (nomes de colunas).")
        if g == 'bar':
            fig = px.bar(
                df,
                x=x,
                y=y,
                color=color,
                title=title,
                orientation=orientation,
                text=text if text else None,
                text_auto=text_auto)
        elif g == 'line':
            fig = px.line(
                df,
                x=x,
                y=y,
                color=color,
                title=title,
                text=text if text else None
            )
        elif g == 'scatter':
            fig = px.scatter(
                df,
                x=x,
                y=y,
                color=color,
                size=size,
                hover_name=hover_name,
                title=title,
                text=text if text else None
            )
    # ----------------------------
    # Gráficos de proporção
    # ----------------------------
    elif g == 'pie':
        if (not names or not values) and (x and y):
            names, values = x, y
        if not names or not values:
            raise ValueError("Para 'pie', informe names e values (ou use x e y).")
        fig = px.pie(
            df,
            names=names,
            values=values,
            color=color,
            title=title,
            hole=0.0,
            hover_name=hover_name
        )
        if text:
            fig.update_traces(textinfo=text)
    # ----------------------------
    # Fallback
    # ----------------------------
    else:
        raise ValueError("Tipo de gráfico não suportado. Use: 'bar', 'line', 'pie' ou 'scatter'.")

    # Layout geral
    fig.update_layout(
        margin=dict(l=16, r=16, t=40, b=16),
        title_x=0.5,
        uniformtext_minsize=10,
        uniformtext_mode='hide')
    # se houver texto, ajusta posição padrão
    if text or text_auto:
        fig.update_traces(textposition='outside')
    return fig    
    
def unicos(df:pd.DataFrame,coluna:str)->int:
    ''' Função recebe um dataframe e uma coluna indicada e 
        retorna os números únicos daquela coluna desejada.'''
    unicos = df[coluna].nunique()
    return unicos

def grafico_avaliacao_maiores(df):
    df2 = agrupamento(
        df,
        agrupador='country_name',
        alvo='aggregate_rating',
        operacao='mean'
    ).sort_values('aggregate_rating', ascending=False)
    df2['aggregate_rating'] = df2['aggregate_rating'].round(2)
    df2.columns = ['Nome do país', 'Nota de Avaliação']
    
    fig = grafico_agrupamento(
        df2.head(15),
        grafico='bar',
        x='Nome do país',
        y='Nota de Avaliação',
        title='Médias de avaliação',
        text='Nota de Avaliação'
    )
    return fig

def grafico_avaliacao_menores(df):
    df2 = agrupamento(
        df,
        agrupador='country_name',
        alvo='aggregate_rating',
        operacao='mean'
    ).sort_values('aggregate_rating', ascending=True)

    df2.columns = ['Nome do país', 'Nota de Avaliação']
    
    fig = grafico_agrupamento(
        df2.tail(15),
        grafico='bar',
        x='Nome do país',
        y='Nota de Avaliação',
        title='Médias de avaliação'
    )
    return fig

def dataframe_paises(df):
    cols = ['country_name','restaurant_id','cuisines','votes']
    df2 = (df.loc[:, cols]
      .groupby('country_name')
      .agg({'restaurant_id': 'nunique',
          'cuisines': 'nunique',       
          'votes': 'mean'})
      .sort_values(['restaurant_id','cuisines','votes'], ascending=False)
      .reset_index())
    df2['votes'] = df2['votes'].round(2)
    df2.columns = ['Nome do país','Número de Restaurantes', 'Culinárias','N° de Avaliações(Média)']
    return df2

def grafico_restaurantes_caros(df):
    df2=(agrupamento(df,agrupador='country_name',alvo='restaurant_id',operacao='nunique',linhas=df['price_range']==4)
     .sort_values('restaurant_id',ascending=False))
    df2.columns = ['Nome do país','Número de restaurantes']
    fig = grafico_agrupamento(df2,grafico='bar',
                          x='Nome do país',
                          y='Número de restaurantes',
                          title='Restaurantes na categoria 4 ou maior(Gourmet)',
                          text='Número de restaurantes')
    return fig

def graficos_valores(df):
    df2 = agrupamento(df,agrupador='country_name',alvo='valor_usd',operacao='mean').sort_values('valor_usd',ascending=False)
    df2['valor_usd']= df2['valor_usd'].round(2)
    df2.columns = ['Nome do país','Valor para duas pessoas em USD($)']
    fig = grafico_agrupamento(df2,grafico='bar',
                          x='Nome do país',
                          y='Valor para duas pessoas em USD($)',
                          title='Valor médio de jantar para duas pessoas',
                          text='Valor para duas pessoas em USD($)')
    return fig

def graficos_paises_cidades(df):
    df2 = agrupamento(df,agrupador='country_name',alvo='city',operacao='nunique').sort_values('city',ascending=False)
    df2.columns =['Nome do país','Cidades registradas']
    fig = grafico_agrupamento(df2,grafico='bar',x='Nome do país',y='Cidades registradas',title='Número de cidades registradas por país',text='Cidades registradas')
    return fig

def ranking_cidades(df, linhas_selecionadas=None):
    cols = ['city', 'restaurant_id','country_name']  
    # aplica filtro se for passado
    if linhas_selecionadas is None:
        base = df.loc[:, cols]
    else:
        base = df.loc[linhas_selecionadas, cols] 
    df2 = (
        base.groupby(['city','country_name'], as_index=False)
            .agg(num_restaurantes=('restaurant_id', 'nunique'),
                 id_mais_antigo=('restaurant_id', 'min'))
            .sort_values(['num_restaurantes', 'id_mais_antigo'], ascending=[False, True])
            .reset_index())
    return df2

def ranking_cidades_1(df):
    cidade = df.loc[0, 'city']
    return cidade

def ranking_cidades_valor(df):
    cols = ['city','restaurant_id', 'valor_usd'] 
    df2 = (df.loc[:,cols].groupby('city', as_index=False)
    .agg(valor_medio=('valor_usd', 'mean'),id_mais_antigo=('restaurant_id', 'min'))
    .sort_values(['valor_medio', 'id_mais_antigo'], ascending=[False, True]).reset_index())
    return df2

def ranking_cidades_cozinhas(df):
    cols = ['city','restaurant_id', 'cuisines'] 
    df2 = (df.loc[:,cols].groupby('city', as_index=False)
           .agg(numero_culinarias=('cuisines', 'nunique'),id_mais_antigo=('restaurant_id', 'min'))
           .sort_values(['numero_culinarias', 'id_mais_antigo'], ascending=[False, True]).reset_index()
    )
    return df2

def grafico_ranking_cidades(df, linhas_selecionadas=None, top_n=20, title='Número de Restaurantes por cidade'):
    cols = ['country_name','city','restaurant_id']
    
    # aplica filtro se vier; senão usa tudo
    if linhas_selecionadas is None:
        base = df.loc[:, cols]
    else:
        base = df.loc[linhas_selecionadas, cols]
    
    df2 = (
        base.groupby(['city','country_name'], as_index=False)
            .agg(
                num_restaurantes=('restaurant_id', 'nunique'),
                id_mais_antigo=('restaurant_id', 'min')
            )
            .sort_values(['num_restaurantes', 'id_mais_antigo'], ascending=[False, True])
            .reset_index(drop=True)
    )
    
    # primeira cidade do ranking
    cidade = df2.loc[0, 'city'] if not df2.empty else None

    # gráfico de barras: x=cidades, y=nº de restaurantes, cor=país
    fig = px.bar(
        df2.head(top_n),
        x='city',
        y='num_restaurantes',
        color='country_name',
        text='num_restaurantes',
        title=title,
        labels={'city': 'Cidade', 'num_restaurantes': 'Nº de Restaurantes', 'country_name': 'País'},
        text_auto=True  # coloca o valor direto nas colunas
    )
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def grafico_cidades_valor(df,linhas_selecionadas=None,top_n=10,title='Valor médio para duas pessoas'):
    cols = ['city','restaurant_id', 'valor_usd','country_name']
    df2 = (df.loc[:,cols].groupby(['city','country_name'], as_index=False)
    .agg(valor_medio=('valor_usd', 'mean'),id_mais_antigo=('restaurant_id', 'min'))
    .sort_values(['valor_medio', 'id_mais_antigo'], ascending=[False, True]).reset_index())
    df2['valor_medio']=df2['valor_medio'].round(2)
    fig = px.bar(
        df2.head(top_n),
        x='city',
        y='valor_medio',
        color='country_name',
        text='valor_medio',
        title=title,
        labels={'city': 'Cidade', 'valor_medio': 'Valor médio para 2 pessoas($)', 'country_name': 'País'},
        text_auto=True  # coloca o valor direto nas colunas
    )
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def grafico_cidades_valor_menores(df,linhas_selecionadas=None,top_n=10,title='Valor médio para duas pessoas'):
    cols = ['city','restaurant_id', 'valor_usd','country_name']
    df2 = (df.loc[:,cols].groupby(['city','country_name'], as_index=False)
    .agg(valor_medio=('valor_usd', 'mean'),id_mais_antigo=('restaurant_id', 'min'))
    .sort_values(['valor_medio', 'id_mais_antigo'], ascending=[False, True]).reset_index())
    df2['valor_medio']=df2['valor_medio'].round(2)
    fig = px.bar(
        df2.tail(top_n),
        x='city',
        y='valor_medio',
        color='country_name',
        text='valor_medio',
        title=title,
        labels={'city': 'Cidade', 'valor_medio': 'Valor médio para 2 pessoas($)', 'country_name': 'País'},
        text_auto=True  # coloca o valor direto nas colunas
    )
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def grafico_cidades_cozinhas(df,linhas_selecionadas=None,top_n=10,title='Variedade de culinárias disponíveis por cidade'):
    cols = ['city','restaurant_id', 'cuisines','country_name']
    df2 = (df.loc[:,cols].groupby(['city','country_name'], as_index=False)
    .agg(num_cozinhas=('cuisines', 'nunique'),id_mais_antigo=('restaurant_id', 'min'))
    .sort_values(['num_cozinhas', 'id_mais_antigo'], ascending=[False, True]).reset_index())
    fig = px.bar(
        df2.head(top_n),
        x='city',
        y='num_cozinhas',
        color='country_name',
        text='num_cozinhas',
        title=title,
        labels={'city': 'Cidade', 'num_cozinhas': 'Número de culinárias disponíveis', 'country_name': 'País'},
        text_auto=True  # coloca o valor direto nas colunas
    )
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def restaurantes_rtg_max_min(df,cuisine='Italian',operacao='max'):
    cols = ['restaurant_name','aggregate_rating','restaurant_id']
    linhas_selecionadas = (df['cuisines'] == cuisine) & (df['votes'] >= 4)
    df2 = (df.loc[linhas_selecionadas,cols].groupby('restaurant_name', as_index=False)
    .agg(media_avaliacao=('aggregate_rating', operacao),id_mais_antigo=('restaurant_id', 'min'))
    .sort_values(['media_avaliacao', 'id_mais_antigo'], ascending=[(operacao == 'min'), True]).reset_index()
    )
    restaurante = df2.loc[0,'restaurant_name']
    return restaurante
    
def nota_rest_rtg_max_min(df,cuisine='Italian',operacao='max'):
    cols = ['restaurant_name','aggregate_rating','restaurant_id']
    linhas_selecionadas = (df['cuisines'] == cuisine) & (df['votes'] >= 4)
    df2 = (df.loc[linhas_selecionadas,cols].groupby('restaurant_name', as_index=False)
           .agg(media_avaliacao=('aggregate_rating', operacao),id_mais_antigo=('restaurant_id', 'min'))
           .sort_values(['media_avaliacao', 'id_mais_antigo'], ascending=[(operacao == 'min'), True])).reset_index()    
    nota = df2.loc[0,'media_avaliacao']
    return nota

def ranking_restaurantes_cuisine(df, cuisine, criterio='max', min_votes=4):
    """
    df        : DataFrame base
    cuisine   : ex. 'Arabian'
    criterio  : 'max' (melhor avaliado) | 'min' (pior avaliado)
    min_votes : inteiro opcional (ex.: 50) para filtrar restaurantes com votos suficientes
    """
    # mantém sua estrutura
    cols = ['restaurant_name','aggregate_rating','restaurant_id',
            'valor_usd','country_name','city','cuisines','votes']
    # filtro base
    linhas_selecionadas = (df['cuisines'] == cuisine)
    if min_votes is not None:
        linhas_selecionadas = linhas_selecionadas & (df['votes'] >= min_votes)
    base = df.loc[linhas_selecionadas, cols]
    # escolhe função de agregação de forma segura
    crit = 'min' if str(criterio).lower() == 'min' else 'max'
    # agrega por restaurante
    df2 = (
        base.groupby('restaurant_name', as_index=False)
            .agg(
                media_avaliacao=('aggregate_rating', crit),
                id_mais_antigo=('restaurant_id', 'min')
            )
            .sort_values(['media_avaliacao', 'id_mais_antigo'],
                         ascending=[(crit == 'min'), True])
            .reset_index(drop=True)
    )
    # merge para puxar valor_usd, país e cidade do registro representativo
    df2 = (
        df2.merge(
            base[['restaurant_name','restaurant_id','valor_usd','country_name','city']],
            left_on=['restaurant_name','id_mais_antigo'],
            right_on=['restaurant_name','restaurant_id'],
            how='left'
        )
        .drop(columns=['restaurant_id'])
    )
    # ajuda pro Streamlit
    df2['valor_usd'] = df2['valor_usd'].round(2)
    df2['help'] = (
        '💰 US$ ' + df2['valor_usd'].astype(str) + ' p/2'
        + ' • 📍 ' + df2['city'].astype(str) + ', ' + df2['country_name'].astype(str)
    )
    return df2

def mostrar_metric_cuisine(df, cuisine, *, min_votes=4, criterio='max'):
    # calcula o ranking
    df2 = ranking_restaurantes_cuisine(df, cuisine, criterio=criterio, min_votes=min_votes)

    # se não voltou nada, mostra placeholder seguro (não quebra a página)
    if df2.empty or pd.isna(df2.loc[0, 'media_avaliacao']):
        st.metric(
            label=f"{cuisine}: —",
            value="—/5.0",
            help="Sem dados após os filtros atuais.")
        return
    st.metric(
        label=f"{cuisine}: {df2.loc[0, 'restaurant_name']}",
        value=f"{df2.loc[0, 'media_avaliacao']:.1f}/5.0",
        help=df2.loc[0, 'help'])
    
def dataframe_restaurantes(df):    
    cols = ['restaurant_id','restaurant_name','cuisines','city','country_name','aggregate_rating','valor_usd','votes']
    df2 = (
    df.loc[:, cols]
            .groupby('restaurant_name', as_index=False)
            .agg({
              'restaurant_id': 'min',
              'cuisines':'first',
              'city': 'first',
              'country_name': 'first',
              'aggregate_rating': 'mean',
              'valor_usd': 'mean',
              'votes': 'sum'
            })
            # ordena: maior nota, ID mais antigo (menor), mais votos
            .sort_values(['aggregate_rating','restaurant_id','votes'],
                       ascending=[False, True, False])
            .reset_index(drop=True)
            )
    # arredonda números
    df2['aggregate_rating'] = df2['aggregate_rating'].round(2)
    df2['valor_usd']        = df2['valor_usd'].round(2)
    # reordena colunas para bater com seus rótulos
    df2 = df2[['restaurant_id','restaurant_name','cuisines','city','country_name','aggregate_rating','valor_usd','votes']]
    # renomeia com segurança (mapeamento)
    df2 = df2.rename(columns={
    'restaurant_id':   'ID do restaurante',
    'restaurant_name': 'Nome do restaurante',
    'cuisines':         'Tipo de Culinária',
    'city':            'Cidade',
    'country_name':    'País',
    'aggregate_rating':'Nota média de avaliação',
    'valor_usd':       'Valor médio para 2 pessoas($)',
    'votes':           'N° de Avaliações'
    })
    return df2
    
def grafico_valor_restaurantes_menor(df):
    cols = ['restaurant_id','valor_usd','restaurant_name','country_name']
    linhas_selecionadas = df['valor_usd'] != 0.0
    df2 = (df.loc[linhas_selecionadas,cols].groupby('restaurant_name', as_index=False)
    .agg(media_valor=('valor_usd', 'mean'),id_mais_antigo=('restaurant_id', 'min'),nome_pais=('country_name','first'))
    .sort_values(['media_valor', 'id_mais_antigo'], ascending=[True, True]))
    df2.columns = ['Nome do Restaurante','Valor médio para 2 p.($)','ID do Restaurante','País']
    df2.reset_index()
    fig = px.bar(df2.head(15), x='Nome do Restaurante',y='Valor médio para 2 p.($)',text='Valor médio para 2 p.($)',title='Os 15 menores preços para 2 pessoas por restaurante',color='País')
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def grafico_valor_restaurantes_maior(df):
    cols = ['restaurant_id','valor_usd','restaurant_name','country_name']
    linhas_selecionadas = df['valor_usd'] != 0.0
    df2 = (df.loc[linhas_selecionadas,cols].groupby('restaurant_name', as_index=False)
    .agg(media_valor=('valor_usd', 'mean'),id_mais_antigo=('restaurant_id', 'min'),nome_pais=('country_name','first'))
    .sort_values(['media_valor', 'id_mais_antigo'], ascending=[False, True]))
    df2.columns = ['Nome do Restaurante','Valor médio para 2 p.($)','ID do Restaurante','País']
    df2.reset_index()
    fig = px.bar(df2.head(15), x='Nome do Restaurante',y='Valor médio para 2 p.($)',text='Valor médio para 2 p.($)',title='Os 15 menores preços para 2 pessoas por restaurante',color='País')
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def grafico_nota_restaurantes_menor(df):
    cols = ['restaurant_id','aggregate_rating','restaurant_name','country_name']
    linhas_selecionadas = df['aggregate_rating'] != 0.0
    df2 = (df.loc[linhas_selecionadas,cols].groupby('restaurant_name', as_index=False)
    .agg(media_nota=('aggregate_rating', 'mean'),id_mais_antigo=('restaurant_id', 'min'),nome_pais=('country_name','first'))
    .sort_values(['media_nota', 'id_mais_antigo'], ascending=[True, True]))
    df2.columns = ['Nome do Restaurante','Nota média de avaliação','ID do Restaurante','País']
    df2.reset_index()
    fig = px.bar(df2.head(15), x='Nome do Restaurante',y='Nota média de avaliação',text='Nota média de avaliação',title='Os 15 piores restaurantes avaliados',color='País')
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def grafico_nota_restaurantes_maior(df):
    cols = ['restaurant_id','aggregate_rating','restaurant_name','country_name']
    linhas_selecionadas = df['aggregate_rating'] != 0.0
    df2 = (df.loc[linhas_selecionadas,cols].groupby('restaurant_name', as_index=False)
    .agg(media_nota=('aggregate_rating', 'mean'),id_mais_antigo=('restaurant_id', 'min'),nome_pais=('country_name','first'))
    .sort_values(['media_nota', 'id_mais_antigo'], ascending=[False, True]))
    df2.columns = ['Nome do Restaurante','Nota média de avaliação','ID do Restaurante','País']
    df2.reset_index()
    fig = px.bar(df2.head(15), x='Nome do Restaurante',y='Nota média de avaliação',text='Nota média de avaliação',title='Os 15 melhores restaurantes avaliados',color='País')
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

def grafico_notas_culinarias(df):
    cols =['restaurant_id','aggregate_rating','cuisines']
    linhas_selecionadas = df['aggregate_rating'] != 0.0
    df2 = df.loc[linhas_selecionadas,cols].groupby('cuisines').agg(media_nota=('aggregate_rating', 'mean'),id_mais_antigo=('restaurant_id', 'min')).sort_values(['media_nota', 'id_mais_antigo'], ascending=[True, True]).reset_index()
    df2['media_nota']=df2['media_nota'].round(2)
    df2.columns = ['Tipo de Culinária','Nota média de avaliação','ID do Restaurante']
    fig = px.bar(df2.head(15), x='Tipo de Culinária',y='Nota média de avaliação',text='Nota média de avaliação',title='As culinárias mais bem avaliadas')
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return fig

import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import streamlit as st

def restaurants_map(
    df,
    *,
    color_col='color',        # coluna que define a cor dos pinos
    cluster=True,                    # ativa/desativa o agrupamento por zoom
    lat_col='latitude',
    lon_col='longitude',
    city_col='city',
    country_col='country_name',
    rating_col='aggregate_rating',
    cuisine_col='cuisines',
    name_col='restaurant_name',
    zoom_start=2,
    show_legend=True                 # mostra uma tabela simples com o mapeamento cor→categoria (no Streamlit)
):
    # seleciona colunas e remove coordenadas nulas
    cols = [c for c in [lat_col, lon_col, city_col, country_col, rating_col, cuisine_col, name_col, color_col] if c in df.columns]
    data = df.loc[:, cols].dropna(subset=[lat_col, lon_col]).copy()

    # normaliza nota (se vier como string)
    if rating_col in data.columns:
        data[rating_col] = pd.to_numeric(data[rating_col], errors='coerce')

    # centro do mapa
    lat_center = data[lat_col].mean()
    lon_center = data[lon_col].mean()
    m = folium.Map(location=[lat_center, lon_center], zoom_start=zoom_start)

    # paleta de cores suportadas pelo folium.Icon
    folium_colors = ['Darkgreen', 'Green', 'Lightgreen', 'Orange', 'Red', 'Darkred']

    # mapeia categoria→cor
    cats = data[color_col].dropna().astype(str).unique().tolist()
    color_map = {c: folium_colors[i % len(folium_colors)] for i, c in enumerate(cats)}

    # marcador simples ou cluster
    container = MarkerCluster().add_to(m) if cluster else m

    # adiciona pinos
    for _, r in data.iterrows():
        cat_val = str(r.get(color_col, ''))
        pin_color = color_map.get(cat_val, 'gray')

        nome  = str(r.get(name_col, '—'))
        nota  = r.get(rating_col, None)
        nota_txt = f"{float(nota):.1f}/5.0" if pd.notna(nota) else "—/5.0"
        culin = str(r.get(cuisine_col, '—'))
        cidade = str(r.get(city_col, '—'))
        pais   = str(r.get(country_col, '—'))

        # popup e tooltip em TEXTO simples
        popup_text = f"{nome}\n⭐ {nota_txt}\n🍽 {culin}\n📍 {cidade}, {pais}"
        tooltip_text = f"{nome} — {nota_txt}"

        folium.Marker(
            location=[r[lat_col], r[lon_col]],
            popup=folium.Popup(popup_text, max_width=280),
            tooltip=tooltip_text,
            icon=folium.Icon(color=pin_color, icon='info-sign')  # ícone padrão (sem HTML)
        ).add_to(container)

    # renderiza o mapa
    folium_static(m, width=1024, height=600)

    # legenda simples no Streamlit (sem HTML): tabela Categoria × Cor
    if show_legend:
        legend_df = pd.DataFrame(
            [(k, v) for k, v in color_map.items()],
            columns=[color_col, 'cor_folium']
        )
        st.caption("Mapa de cores dos marcadores:")
        st.dataframe(legend_df, use_container_width=True)