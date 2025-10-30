import pandas as pd
import numpy as np
import inflection
import plotly.express as px
from typing import Optional
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

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
    fig = px.bar(df2.head(15), x='Nome do Restaurante',y='Valor médio para 2 p.($)',text='Valor médio para 2 p.($)',title='Os 15 maiores preços para 2 pessoas por restaurante',color='País')
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

def restaurants_map(
    df,
    *,
    lat_col='latitude',
    lon_col='longitude',
    name_col='restaurant_name',
    rating_col='aggregate_rating',
    cuisine_col='cuisines',
    city_col='city',
    country_col='country_name',
    color_col='cor',          # <- cor já presente no df
    cluster=True,             # agrupa ao afastar o zoom
    zoom_start=2,
    max_points=5000,          # limite p/ performance na nuvem
    use_circle=True           # CircleMarker é mais leve
):
    """
    Desenha o mapa de restaurantes com marcadores coloridos via df['cor'].
    Limita a amostra a max_points para evitar travar (especialmente no Streamlit Cloud).
    """

    # --- Seleção mínima de colunas e tipagem ---
    cols = [c for c in [lat_col, lon_col, name_col, rating_col, cuisine_col, city_col, country_col, color_col] if c in df.columns]
    data = df.loc[:, cols].copy()

    # garante numéricos
    for c in [lat_col, lon_col, rating_col]:
        if c in data.columns:
            data[c] = pd.to_numeric(data[c], errors='coerce')

    # remove coordenadas inválidas
    data = data.dropna(subset=[lat_col, lon_col])
    if data.empty:
        return st_folium(folium.Map(location=[0, 0], zoom_start=zoom_start), width=1024, height=600)

    # --- downsample leve para não travar (se exceder max_points) ---
    if isinstance(max_points, int) and max_points > 0 and len(data) > max_points:
        # amostragem estratificada simples por cor (mantém proporção das cores)
        data = (
            data.groupby(color_col, group_keys=False)
                .apply(lambda g: g.sample(frac=min(1.0, max_points / len(data)), random_state=42))
        )

    # centro do mapa
    lat_center = float(data[lat_col].mean())
    lon_center = float(data[lon_col].mean())
    m = folium.Map(location=[lat_center, lon_center],zoom_start=zoom_start,tiles="CartoDB positron")

    # normalização básica de nomes de cores aceitos pelo Folium
    allowed = {
        'red','blue','green','purple','orange','darkred','lightred','beige',
        'darkblue','darkgreen','cadetblue','darkpurple','pink','lightblue',
        'lightgreen','gray','black','lightgray'
    }
    pt_alias = {'azul':'blue','verde':'green','vermelho':'red','laranja':'orange','rosa':'pink','cinza':'gray'}
    def norm_color(v):
        c = str(v).strip().lower()
        c = pt_alias.get(c, c)
        return c if c in allowed else 'blue'

    container = MarkerCluster().add_to(m) if cluster else m

    # iteração leve (CircleMarker é mais rápido que Icon)
    for r in data.itertuples(index=False):
        pin_color = norm_color(getattr(r, color_col, 'blue'))
        nome  = str(getattr(r, name_col, '—'))
        culin = str(getattr(r, cuisine_col, '—')) if cuisine_col in data.columns else '—'
        cidade = str(getattr(r, city_col, '—')) if city_col in data.columns else '—'
        pais   = str(getattr(r, country_col, '—')) if country_col in data.columns else '—'
        nota   = getattr(r, rating_col, None) if rating_col in data.columns else None
        nota_txt = f"{float(nota):.1f}/5.0" if pd.notna(nota) else "—/5.0"

        popup_text = f"{nome}\n⭐ {nota_txt}\n🍽 {culin}\n📍 {cidade}, {pais}"
        tooltip_text = f"{nome} — {nota_txt}"

        lat = float(getattr(r, lat_col))
        lon = float(getattr(r, lon_col))

        if use_circle:
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                popup=popup_text,
                tooltip=tooltip_text,
                color=pin_color,
                fill=True,
                fill_color=pin_color,
                fill_opacity=0.7
            ).add_to(container)
        else:
            folium.Marker(
                location=[lat, lon],
                popup=popup_text,
                tooltip=tooltip_text,
                icon=folium.Icon(color=pin_color, icon='info-sign')
            ).add_to(container)

    # render robusto
    return st_folium(m, width=1024, height=600)
