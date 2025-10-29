#=======================================================================================
### Importações e Função de Limpeza
#=======================================================================================
import pandas as pd
import streamlit as st
import numpy as np
import inflection
from PIL import Image
from modules.cleaning import limpar_dataframe, remover_duplicatas, rename_columns, country_name, create_price_type, color_name, mudar_coluna, converter_usd
from modules.charts import unicos,agrupamento,grafico_agrupamento,grafico_avaliacao_maiores, grafico_avaliacao_menores,dataframe_paises,grafico_restaurantes_caros,graficos_valores,graficos_paises_cidades
st.set_page_config(page_title="Países", page_icon="🌏", layout="wide")
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
st.header('🗺🌏 Visão Países')
with st.container():
    st.subheader('Overall Metrics')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df2 = agrupamento(df1, agrupador='country_name',alvo='city',operacao='nunique').sort_values('city', ascending=False).reset_index()
        col1.metric('País +Cidades reg.', df2.loc[0,'country_name'])
    with col2:
        df2 = agrupamento(df1,agrupador='country_name', alvo='restaurant_id',operacao='nunique').sort_values('restaurant_id',   ascending=False).reset_index() 
        col2.metric('País +Rest. reg.', df2.loc[0,'country_name'])
    with col3:
        df2 = agrupamento(df1,agrupador='country_name', alvo='restaurant_id',operacao='nunique',linhas=df1['price_range'] == 4).sort_values('restaurant_id', ascending=False).reset_index()
        col3.metric('País +Rest PR=4', df2.loc[0,'country_name'])
    with col4:
        df2 = agrupamento(df1,agrupador='country_name', alvo='cuisines',operacao='nunique').sort_values('cuisines',ascending=False).reset_index()
        col4.metric('País +Culinárias.', df2.loc[0,'country_name'])
    with col5:
        df2 = agrupamento(df1,agrupador='country_name', alvo='votes',operacao='nunique').sort_values('votes',ascending=False).reset_index()
        col5.metric('País +Avaliações.', df2.loc[0,'country_name'])
    with col6:
        df2 = agrupamento(df1,agrupador='country_name', alvo='votes',operacao='mean').sort_values('votes',ascending=False).reset_index()
        col6.metric('País Maior Med.Aval.', df2.loc[0,'country_name'])
with st.container():
    st.subheader('Avaliação por países')
    fig = grafico_avaliacao_maiores(df1)
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.subheader('Dados dos países')
    st.dataframe(dataframe_paises(df1))
            
with st.container():
    st.subheader('Valores e restaurantes')
    col1,col2 = st.columns(2)
    with col1:
        fig = grafico_restaurantes_caros(df1)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = graficos_valores(df1)
        st.plotly_chart(fig, use_container_width=True)

with st.container():
    st.subheader('Cidades registradas por país')
    fig = graficos_paises_cidades(df1)
    st.plotly_chart(fig, use_container_width=True)