import streamlit as st
import pandas as pd
import numpy as np
import inflection
from PIL import Image
from pathlib import Path
from textwrap import dedent
from modules.cleaning import limpar_dataframe, remover_duplicatas, rename_columns, country_name, create_price_type, color_name, mudar_coluna, converter_usd
from modules.charts import unicos, restaurants_map

st.set_page_config(page_title="Home", page_icon="🏡", layout="wide")
#=======================================================================================    
### Dataframe e Transformação de dados
#=======================================================================================
# Upload do arquivo
df = pd.read_csv('zomato.csv')
df1 = df.copy()

# Renomeando colunas para minúsculo e trocando espaços por underlines
df1 = rename_columns(df1)
df1 = limpar_dataframe(df1, dropna_mode = 'any')
df1 = remover_duplicatas(df1, subset='restaurant_id')

# Concertando valor de número incorreto pela mediana
linha_selecionada = df1['restaurant_id'] == 16608070
df1.loc[linha_selecionada,'average_cost_for_two']= 45

# Criando a coluna Country Name
df1['country_name'] = df1['country_code'].apply(country_name)

# Criando a coluna Categoria de Comida
df1['categoria_de_comida'] = df1['price_range'].apply(create_price_type)

# Criando a coluna Cor
df1['color'] = df1['rating_color'].apply(color_name)

# Mudando as colunas de lugar 
df1 = mudar_coluna(df1,'color',-3)
df1 = mudar_coluna(df1,'categoria_de_comida',-5)
df1 = mudar_coluna(df1,'country_name',3)

# Separando os nomes da coluna 'cuisines'
df1["cuisines"]=df1.loc[:,"cuisines"].apply(lambda x: x.split(",")[0])

# Padronizando os valores de 'average_cost_for_two' para USD
df1 = converter_usd(df1, coluna_valor='average_cost_for_two', coluna_moeda='currency')
#=======================================================================================
# Barra Lateral
#=======================================================================================
image = Image.open("logo_fome_zero.png")
st.sidebar.image(image, width=120)
st.sidebar.markdown("### Fome Zero")
st.sidebar.markdown("## A melhor maneira de você matar a sua fome")
st.sidebar.markdown("---")

#=======================================================================================
# Layout no Streamlit
#=======================================================================================
st.title("Dashboard da Fome Zero")
st.caption("Confira aqui as melhores opções de restaurantes, preços e avaliações em diversos países, cidades e tipos de culinária.")

st.divider()

with st.container():
    st.subheader('Informações Gerais')
    col1,col2,col3,col4,col5=st.columns(5)
    with col1:
        col1.metric('Nº Restaurantes reg.',unicos(df1,'restaurant_id'))
    with col2:
        col2.metric('Nº Países reg.',unicos(df1,'country_name'))
    with col3:
        col3.metric('Nº Cidades reg.',unicos(df1,'city'))
    with col4:
        col4.metric('Nº de aval. feitas',unicos(df1,'votes'))
    with col5:
        col5.metric('Nº Culinárias reg.',unicos(df1,'cuisines'))

with st.container():
    st.subheader("🌎 Mapa — Restaurantes")
    cluster_on = st.checkbox("Agrupar marcadores (MarkerCluster)", value=True)
    color_by = st.selectbox("Colorir pinos por", ["country_name", "cuisines"], index=0)
    restaurants_map( df1,
                color_col='color',
                cluster=cluster_on,
                lat_col='latitude', lon_col='longitude',
                city_col='city', country_col='country_name',
                rating_col='aggregate_rating', cuisine_col='cuisines',
                name_col='restaurant_name',
                zoom_start=2,
                show_legend=True)
                
with st.container():    
    st.markdown(dedent("""
    ### Como usar este Dashboard
    
    - **Visão País**
      - Panorama por país: nº de restaurantes, preço médio p/2 e nota média.
    
    - **Visão Cidades**
      - Ranking de cidades: variedade, valor médio e concentração de restaurantes.
    
    - **Visão Cozinhas**
      - Melhores/piores restaurantes por tipo de culinária, com métricas e tooltips (preço, cidade, país).
    
    > Dica: use os filtros no topo de cada aba para refinar por país, cidade, nota mínima e faixa de preço.
    """))
    
    # Atalhos (mantive a navegação multipáginas, só ajustei rótulos)
    st.subheader("Atalhos")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.page_link("pages/1_País.py", label="🌍 Visão País", icon=":material/insights:")
    with c2:
        st.page_link("pages/2_Cidades.py", label="🏙️ Visão Cidades", icon=":material/trending_up:")
    with c3:
        st.page_link("pages/3_Cozinhas.py", label="🍽️ Visão Cozinhas", icon=":material/restaurant:")
