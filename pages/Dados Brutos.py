import streamlit as st
import pandas as pd
import requests
import time

@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')


def mensagem_sucesso():
    sucesso = st.success(f'Arquivo baixado com sucesso!', icon="✅")
    time.sleep(6)
    sucesso.empty()


st.title('Dados Brutos')
url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

#Adicionando filtros
with st.expander('Colunas'):
    colunas = st.multiselect('Seleciona as colunas', list(dados.columns), list(dados.columns))

#Criando filtros da barra lateral
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Selecione os Produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Categorias'):
    categoria_produto = st.multiselect('Selecione as Categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Frete da Venda'):
    frete = st.slider('Selecione o Valor do Frete', 0, 250, (0, 250))

with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a Data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o Vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da Compra'):
    local_da_compra = st.multiselect('Selecione o Estado da Compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da Compra'):
    avaliacao_compra = st.slider('Selecione a Avaliação da Compra', 1, 5, (1, 5))

with st.sidebar.expander('Tipo de Pagamento'):
    pagamento = st.multiselect('Selecione o Método de Pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de Parcelas'):
    parcelas = st.slider('Selecione a Quantidade de Parcelas', 1, 24, (1, 24))


#Filtrando o dataframe
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria_produto and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local_da_compra and \
@avaliacao_compra[0] <= `Avaliação da compra` <= @avaliacao_compra[1] and \
`Tipo de pagamento` in @pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]



st.dataframe(dados_filtrados)
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em CSV', data=converte_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)
    
#[theme]
base="light"
primaryColor="#3dd1e6"
