#=======================================================================================
### Importações e Função de Limpeza
#=======================================================================================
import pandas as pd
import streamlit as st
import numpy as np
import inflection
import plotly.express as px
from PIL import Image
from modules.cleaning import limpar_dataframe, remover_duplicatas, rename_columns, country_name, create_price_type, color_name, mudar_coluna, converter_usd
from modules.charts import restaurantes_rtg_max_min, nota_rest_rtg_max_min, ranking_restaurantes_cuisine, dataframe_restaurantes, grafico_valor_restaurantes_menor, grafico_valor_restaurantes_maior, grafico_nota_restaurantes_menor, grafico_nota_restaurantes_maior, grafico_notas_culinarias, mostrar_metric_cuisine

st.set_page_config(page_title="Cuisines", page_icon="🥘", layout="wide")
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
image = Image.open('logo_fome_zero.png')
st.sidebar.image(image, width =120)
st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown('### A melhor maneira de você matar a sua fome')
st.sidebar.markdown("""---""")

country_options = st.sidebar.multiselect(
    'Quais países deseja selecionar?',
    ['Philippines', 'Brazil', 'Australia', 'USA',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'],
    default = ['Philippines', 'Brazil', 'Australia', 'USA',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'])
cuisine_options = st.sidebar.multiselect(
    'Quais tipos de culinárias deseja selecionar?',
    ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'Mineira', 'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian',
       'Author', 'Gourmet Fast Food', 'Lebanese', 'Modern Australian',
       'African', 'Coffee and Tea', 'Australian', 'Middle Eastern',
       'Malaysian', 'Tapas', 'New American', 'Pub Food', 'Southern',
       'Diner', 'Donuts', 'Southwestern', 'Sandwich', 'Irish',
       'Mediterranean', 'Cafe Food', 'Korean BBQ', 'Fusion', 'Canadian',
       'Breakfast', 'Cajun', 'New Mexican', 'Belgian', 'Cuban', 'Taco',
       'Caribbean', 'Polish', 'Deli', 'British', 'California', 'Others',
       'Eastern European', 'Creole', 'Ramen', 'Ukrainian', 'Hawaiian',
       'Patisserie', 'Yum Cha', 'Pacific Northwest', 'Tea', 'Moroccan',
       'Burmese', 'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian',
       'Continental', 'South Indian', 'North Indian', 'Salad',
       'Finger Food', 'Mandi', 'Turkish', 'Kerala', 'Pakistani',
       'Biryani', 'Street Food', 'Nepalese', 'Goan', 'Iranian', 'Mughlai',
       'Rajasthani', 'Mithai', 'Maharashtrian', 'Gujarati', 'Rolls',
       'Momos', 'Parsi', 'Modern Indian', 'Andhra', 'Tibetan', 'Kebab',
       'Chettinad', 'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi',
       'Afghan', 'Lucknowi', 'Charcoal Chicken', 'Mangalorean',
       'Egyptian', 'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian',
       'Western', 'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian',
       'Balti', 'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji',
       'South African', 'Drinks Only', 'Durban', 'World Cuisine',
       'Izgara', 'Home-made', 'Giblets', 'Fresh Fish', 'Restaurant Cafe',
       'Kumpir', 'Döner', 'Turkish Pizza', 'Ottoman', 'Old Turkish Bars',
       'Kokoreç'],
    default = ['Italian','Brazilian','American','Italian','Arabian','Japanese','BBQ','Home-made'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Júlio Takeichi')

#Filtro de país
linhas_selecionadas = df1['country_name'].isin(country_options)
df1= df1.loc[linhas_selecionadas,:]
#Filtro culinárias
linhas_selecionadas = df1['cuisines'].isin(cuisine_options)
df1= df1.loc[linhas_selecionadas,:]
#=======================================================================================
# Layout no Streamlit
#=======================================================================================
st.header('🥘Visão Cozinhas')
with st.container():
    st.subheader('Overall Metrics - Melhores Restaurantes')
    col1,col2,col3,col4,col5,col6= st.columns(6)
    with col1:
        mostrar_metric_cuisine(df1, "Italian", min_votes=4, criterio='max')
    with col2:
        mostrar_metric_cuisine(df1, "American", min_votes=4, criterio='max')
    with col3:
        mostrar_metric_cuisine(df1, "Arabian", min_votes=4, criterio='max')
    with col4:
        mostrar_metric_cuisine(df1, "Japanese", min_votes=4, criterio='max')
    with col5:
        mostrar_metric_cuisine(df1, "Brazilian", min_votes=4, criterio='max')
    with col6:
        mostrar_metric_cuisine(df1, "Home-made", min_votes=4, criterio='max')
       
with st.container():
    st.subheader('Top 20 melhores restaurantes')
    df2 = dataframe_restaurantes(df1)
    st.dataframe(df2.head(20))

with st.container():
    col1,col2 = st.columns(2)
    with col1:
        fig = grafico_valor_restaurantes_menor(df1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = grafico_valor_restaurantes_maior(df1)
        st.plotly_chart(fig, use_container_width=True)
with st.container():
    col1,col2 = st.columns(2)
    with col1:
        fig=grafico_nota_restaurantes_menor(df1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig=grafico_nota_restaurantes_maior(df1)
        st.plotly_chart(fig, use_container_width=True)
with st.container():
        fig = grafico_notas_culinarias(df1)
        st.plotly_chart(fig, use_container_width=True)