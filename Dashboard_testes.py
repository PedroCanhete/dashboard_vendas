#Bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

#Funções
# Função para formatar os valores apresentados nos gráficos
def formata_numero(valor, prefixo= ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


# Função para calcular os limites do eixo X com base nos dados plotados
def definir_limites_eixo_x(dados, coluna, x_margem=0.1):
    """
    Define os limites do eixo X com base nos dados filtrados.
    - dados: DataFrame filtrado.
    - coluna: Coluna numérica a ser analisada.
    - margem: Proporção adicional para incluir no limite máximo.
    """
    # Define os valores mínimos e máximos
    x_valor_min = dados[coluna].min()
    x_valor_max = dados[coluna].max()

    # Define uma margem para garantir que os valores não fiquem no limite exato
    x_margem_valor = (x_valor_max - x_valor_min) * x_margem
    return [max(0, x_valor_min - x_valor_max), x_valor_max - x_margem_valor]


# Função para calcular os limites do eixo Y com base nos dados plotados
def definir_limites_eixo_y(dados, coluna, y_margem=0.1):
    """ 
    Define os limites do eixo Y com base nos dados filtrados.
    - dados: DataFrame filtrado.
    - coluna: Coluna numérica a ser analisada.
    - margem: Proporção adicional para incluir no limite máximo.
    """
    # Definindo os valores mínimos e máximos
    y_min_val = dados[coluna].min()
    y_max_val = dados[coluna].max()
    
    # Definindo uma margem para garantir que os valores não fiquem no limite exato
    y_margem_valor = (y_max_val - y_min_val) * y_margem
    return [max(0, y_min_val - y_margem_valor), y_max_val + y_margem_valor]



#Cores
AZUL1, AZUL2, AZUL3, AZUL4, AZUL5, AZUL6 = '#174A7E', '#4A81BF', "#6495ED", '#2596BE', '#94AFC5', '#CDDBF3'
CINZA1, CINZA2, CINZA3, CINZA4, CINZA5, BRANCO = '#231F20', '#414040', '#555655', '#A6A6A5', '#BFBEBE', '#FFFFFF'
VERMELHO1, VERMELHO2, LARANJA1 = '#C3514E',	'#E6BAB7',	'#F79747'
VERDE1, VERDE2, VERDE3 = '#0C8040',	'#9ABB59', '#9ECCB3'

cores_graficos = [AZUL2, VERMELHO2, CINZA3, LARANJA1, VERDE2]



###### Código Principal

###### Título
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

###### Leitura dos dados apresentados a partir da biblioteca requests
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul'] #Essa lista das regiões servirá para utilizar na filtragem dos gráficos. Estamos fazendo isso previamente pois a API consegue nos retornar a filtragem de região e ano pelo link, mas não de vendedor. Portanto, vamos usar esse filtro pelo link anteriormente a de vendedor.


###### Filtragem na Barra Lateral
#Título barra lateral
st.sidebar.title('Filtros')

#Filtro de região
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

#Filtro de anos
todos_os_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_os_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', min_value=2020, max_value=2023)


###### Importando os dados da url
query_string = {'regiao':regiao.lower(), 'ano': ano} #Query dos filtros definidos acima
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format=('%d/%m/%Y')) #transformando a coluna de datas para formato datetime e podermos gerar um gráfico de linhas em cima do faturamento MENSAL
dados['Categoria do Produto'] = dados['Categoria do Produto'].str.title()


#Filtro Vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
#Configuração para que caso não selecionemos nenhum vendedor, deixaremos todos marcados
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
#Caso selecionemos algum vendedor, tudo que acontecerá abaixo será com as informações dele, caso não, será de todos.


###### Tabelas
### Tabelas Aba RECEITA

#Tabela Gráfico de Barras
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False) #Aqui estamos removendo os dados duplicados de latitude e longitude dos estados, pegando as colunas de local da compra, latitude e longitude e, dando um merge com a própria tabela que foi definida anteriormentte com os valores de vendas agrupados

#Tabela Gráfico de Linhas
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))[['Preço']].sum().reset_index() #Após transformar a coluna de datas para datetime, estamos a transformando no índice de nossa nova tabela 'receita_mensal'; junto disso, estamos agrupando os dados a partir do mês q está em nosso índice
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()
receita_mensal['Mes_Abreviado'] = receita_mensal['Mes'].str[:3]

#Tabela Gráfico de Barras
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

#Tabela Gráfico de Area
dados_estados = dados.copy()
dados_estados['Data da Compra'] = dados_estados['Data da Compra'].dt.year
receita_area_estados = dados_estados.groupby(['Local da compra', 'Data da Compra'])[['Preço']].sum().reset_index()
top_5_compradores = receita_area_estados.groupby('Local da compra')['Preço'].sum().nlargest(5).index
receita_area_estados_top = receita_area_estados[receita_area_estados['Local da compra'].isin(top_5_compradores)]



### Tabelas aba QUANTIDADE DE VENDAS
#Tabela gráfico de mapa com a quantidade de vendas por estado + 05 estados com a maior quantidade de vendas
vendas_por_estado = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_por_estado = vendas_por_estado.rename(columns={'Preço': 'Quantidade de Vendas'})
vendas_por_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_por_estado, left_on='Local da compra', right_index=True).sort_values('Quantidade de Vendas', ascending=False)

#Tabela gráfico de linhas com a quantidade de vendas mensal
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count()).reset_index()
vendas_mensal = vendas_mensal.rename(columns={'Preço': 'Quantidade de Vendas'})
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year

#Tabela gráfico de barras com a quantidade de vendas por categoria de produto
vendas_produto = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending=False))
vendas_produto = vendas_produto.rename(columns={'Preço': 'Quantidade de Vendas'})
vendas_produto = vendas_produto.reset_index()



### Tabelas aba VENDEDORES
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))



###### Gráficos
#### Gráfico aba 1
#Gráfico de Barras horizontais com as vendas por categoria
fig_receita_categoria = px.bar(receita_categorias, 
                               x='Preço', y=receita_categorias.index, 
                               title='Receita por Categoria', 
                               orientation='h', 
                               color=receita_categorias.index)
eixo_x_receita_categoria = definir_limites_eixo_x(receita_categorias, 'Preço', x_margem=0)
fig_receita_categoria.update_layout(showlegend=False,
    title={
        'font':{'size': 20, 'weight':'bold'},
        'x': 0.3,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis={
        'range': eixo_x_receita_categoria,
        'title': {'text': 'Valores', 'font': {'size': 16, 'weight': 'bold'}},
        'tickfont': {'family': 'Arial', 'size': 12, 'weight': 'bold'}
    },
    yaxis={
        'title': {'text': 'Categoria', 'font': {'size': 16, 'weight': 'bold'}},
        'tickfont': {'family': 'Arial', 'size': 12, 'weight': 'bold'}
    }
)
fig_receita_categoria.update_traces(texttemplate='R$ %{x:.2s}',
                                    hovertemplate='Categoria: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>')


#Gráfico de Linha com as vendas por mês em cada ano
fig_receita_mensal = px.line(receita_mensal, x='Mes_Abreviado', y='Preço',
                             markers=True, range_y=(0, receita_mensal.max()),
                             color='Ano', line_dash='Ano', line_shape='spline',
                             title='Receita Mensal')
eixo_y_receita_mensal = definir_limites_eixo_y(receita_mensal, 'Preço')
fig_receita_mensal.update_layout(
    title={
        'font':{'size': 20, 'weight':'bold'},
        'x':0.3,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis={
        'title':{'text':'Meses', 'font':{'size':16, 'weight':'bold'}},
        'tickvals':[2, 5, 8, 11],
        'ticktext':['Março', 'Junho', 'Setembro', 'Dezembro'],
        'tickfont':{'family':'Arial', 'size':12, 'weight':'bold'},
        'tickangle':-45
    },
    yaxis={
        'title':{'text':'Receita', 'font':{'size':16,'weight':'bold'}},
        'range':eixo_y_receita_mensal,
        'tickfont':{'family':'Arial', 'size':12,'weight':'bold'}
    },
    legend={
        'font':{'size':16},
        'title':{'font':{'size':16}}
    }
)
fig_receita_mensal.update_traces(hovertemplate='%{fullData.name}<br>%{x}<br><b>Receita Mensal: R$ %{y:,.2f}</b>'.replace(',', '.'))




#Gráfico de Barras com as vendas por estados
fig_receita_estados = px.bar(receita_estados.head(5), 
                             x='Local da compra', y='Preço', 
                             title='Top 5 Estados (Por Receita)',
                             color='Local da compra',
                             color_discrete_map={'SP': AZUL2, 'RJ': VERMELHO2, 'MG': CINZA3, 'RS': LARANJA1, 'PR': VERDE2})
fig_receita_estados.update_layout(showlegend=False,
    title={
        'font':{'size': 20, 'weight':'bold'},
        'x': 0.3,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis={
        'title': {'text': 'Local da Compra', 'font': {'size': 16, 'weight': 'bold'}},
        'tickfont': {'family': 'Arial', 'size': 12, 'weight': 'bold'}
    },
    yaxis={
        'title': {'text': 'Receita', 'font': {'size': 16, 'weight': 'bold'}},
        'tickfont': {'family': 'Arial', 'size': 12, 'weight': 'bold'},
        
    },
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)
fig_receita_estados.update_traces(texttemplate='<b>R$ %{y:.2s}</b>',
                                  hovertemplate='Local da Compra: %{x}<br><b>Receita: R$ %{y:,.2f}</b><extra></extra>')

#Gráfico de área com as vendas por estados


#Gráfico de Mapa com as vendas por estados
fig_mapa_receita = px.scatter_geo(receita_estados, lat='lat', lon='lon', 
                                  scope='south america', size= 'Preço', 
                                  template= 'seaborn', hover_name='Local da compra', 
                                  hover_data={'lat': False, 'lon': False},
                                  title='Receita Por Estado')
fig_mapa_receita.update_layout(title_font_size=20)
fig_mapa_receita.update_traces(hovertemplate='<b>%{hovertext}</b><br>Receita Estado: R$ %{marker.size:,.2f}'.replace(',', '.'),
                               hovertext=receita_estados['Local da compra'])



### Gráficos aba 2
#Gráfico de mapa com a quantidade de vendas por estado
fig_mapa_vendas = px.scatter_geo(vendas_por_estado, lat='lat', lon='lon',
                                 scope='south america', size='Quantidade de Vendas',
                                 template='seaborn', hover_name='Local da compra',
                                 hover_data= {'lat':False, 'lon':False},
                                 title='Quantidade de Vendas por Estado')
fig_mapa_vendas.update_layout(title_font_size=20)

#Gráfico de linha com a quantidade de vendas por mês
fig_vendas_mensal = px.line(vendas_mensal, x='Mês', y='Quantidade de Vendas', markers=True,
                            range_y=(0, vendas_mensal.max()),
                            color='Ano', line_dash='Ano',
                            title='Quantidade de Vendas Mensais')
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de Vendas', xaxis_title='Vendas', title_font_size=20)

#Gráfico de barras com os 5 estados com a maior quantidade de vendas
fig_05_estados_vendas = px.bar(vendas_por_estado.head(5), x='Local da compra',
                               y='Quantidade de Vendas',
                               text_auto=True,
                               title='Top 5 Estados com a maior quantidade de Vendas',
                               color='Local da compra')
fig_05_estados_vendas.update_layout(yaxis_title='Quantidade de Vendas', xaxis_title='Estados', title_font_size=20)

#Gráfico de barras com a quantidade de vendas por categoria de produto
fig_vendas_categorias = px.bar(vendas_produto,
                               x='Quantidade de Vendas',
                               y='Categoria do Produto', 
                               text_auto=True,
                               title='Quantidade de Vendas por Categorias',
                               color='Categoria do Produto',
                               orientation='h')
fig_vendas_categorias.update_layout(xaxis_title='Quantidade de Vendas', yaxis_title='Categoria Produtos', showlegend=False, title_font_size=20)


#Gráficos aba 3
# No caso da 3 aba de vendedores, como é uma parte interativa, precisaremos definir os gráficos diretamente na aba 3, pois definimos a interatividade na 3ª aba com a função st.numer_input()



###### Visualização dos dados
#Abas a partir das colunas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita (Anual)', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_receita_categoria, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de Vendas (Anual)', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_mapa_receita, use_container_width=True)

        

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita (Anual)', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_05_estados_vendas, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de Vendas (Anual)', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)



with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5) #definindo a interatividade dos vendedores, sendo os parâmetros incluídos o numero minimo, máximo e o padrão que irá aparecer
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita (Anual)', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum', y= vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True, orientation='h',
                                        title=f' Top {qtd_vendedores} vendedores (receita)'
                                        )
        fig_receita_vendedores.update_layout(yaxis_title='Vendedor', xaxis_title='Receita das Vendas')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de Vendas (Anual)', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x='count', y= vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True, orientation='h',
                                        title=f' Top {qtd_vendedores} vendedores (quantidade de vendas)'
                                        )
        fig_vendas_vendedores.update_layout(yaxis_title='Vendedor', xaxis_title='Quantidade de Vendas')
        st.plotly_chart(fig_vendas_vendedores)

