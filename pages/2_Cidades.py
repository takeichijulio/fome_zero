#=======================================================================================
### Importações e Função de Limpeza
#=======================================================================================
import pandas as pd
import streamlit as st
import numpy as np
import inflection
from PIL import Image
from modules.cleaning import limpar_dataframe, remover_duplicatas, rename_columns, country_name, create_price_type, color_name, mudar_coluna, converter_usd
from modules.charts import unicos ,agrupamento ,grafico_agrupamento ,ranking_cidades ,ranking_cidades_1 ,ranking_cidades_valor ,ranking_cidades_cozinhas ,graficos_paises_cidades ,grafico_ranking_cidades, grafico_cidades_valor, grafico_cidades_cozinhas, grafico_cidades_valor_menores
st.set_page_config(page_title="Cidades", page_icon="🏙", layout="wide")
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
    'Quais os países que deseja selecionar?',
    ['Philippines', 'Brazil', 'Australia', 'USA',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'],
    default = ['Philippines', 'Brazil', 'Australia', 'USA',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
       'Sri Lanka', 'Turkey'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Júlio Takeichi')

#Filtro de país
linhas_selecionadas = df1['country_name'].isin(country_options)
df1= df1.loc[linhas_selecionadas,:]
#=======================================================================================
# Layout no Streamlit
#=======================================================================================
st.header('🏙 Visão Cidades')
with st.container():
    st.subheader('Overall Metrics')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df2 = ranking_cidades(df1)
        col1.metric('Cidade +Rest', ranking_cidades_1(df2))    
    with col2:
        df2 = ranking_cidades(df1, linhas_selecionadas= df1['aggregate_rating'] > 4)
        col2.metric('Cidade +Rest N4', ranking_cidades_1(df2))
    with col3:
        df2 = ranking_cidades(df1, linhas_selecionadas=df1['aggregate_rating'] < 2.5)
        col3.metric('Cidade +Rest N2.5', ranking_cidades_1(df2))
    with col4:
        df2 = ranking_cidades_valor(df1)
        col4.metric('Cid. maior valor med.' ,df2.loc[0, 'city'])
    with col5:
        df2 = ranking_cidades_cozinhas(df1)
        col5.metric('Cid. maior nº cozinhas',df2.loc[0, 'city'])
    with col6:
        df2 = ranking_cidades(df1, linhas_selecionadas=df1['has_online_delivery'] == 1)
        col6.metric('Cid.+Rest Delivery',ranking_cidades_1(df2))        
with st.container():
    fig = grafico_ranking_cidades(df1,top_n=45,title='Número de restaurantes registrados por cidade')
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    col1,col2 = st.columns(2)
    with col1:
        fig=grafico_ranking_cidades(df1,linhas_selecionadas=df1['aggregate_rating']>4,top_n=10,title='Top 10 Cidades com mais restaurantes(Gourmet)')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig=grafico_ranking_cidades(df1,linhas_selecionadas = df1['aggregate_rating']<2.5,top_n=10,title='Top 10 Cidades com mais restaurantes com nota 2.5 ou menor')
        st.plotly_chart(fig, use_container_width=True)

with st.container():
    col1,col2 = st.columns(2)
    with col1:
        fig=grafico_cidades_valor(df1,top_n=10,title='Maiores valores médios para 2 pessoas por cidade')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig=grafico_cidades_valor_menores(df1,top_n=10,title='Menores valores médios para 2 pessoas por cidade')
        st.plotly_chart(fig, use_container_width=True)

with st.container():
        fig=grafico_cidades_cozinhas(df1,top_n=10)
        st.plotly_chart(fig, use_container_width=True)
    