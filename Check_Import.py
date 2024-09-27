from datetime import date, timedelta
import streamlit as st
import pandas as pd
import requests
import pyodbc
import json

data_formatada = ""

# Configuração da conexão com o banco de dados
connection_string = (
    'Driver={SQL Server};'
    'Server=tcp:oikoswm.database.windows.net,1433;'
    'Database=Oikos;'
    'Uid=oikosroot;'
    'Pwd=AgpPs@7$2qL0?&of;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=60;'
)

# Função para conectar ao banco de dados e buscar os tickers
def get_tickers():
    conn = None
    
    query = f"""
    SELECT DISTINCT ticker_cmd 
    FROM [dbo].[posicoes_diarias] 
    WHERE jurisdicao = '{opcao_selecionada}' 
    AND tipo_ativo NOT in('Caixa', 'caixaB', 'lci','lca','lf','lc', 'lig', 'cdb', 'lft','titulo' )
    AND data_ref = '{data_formatada}'
    AND ticker_cmd NOT LIKE '%\%%' ESCAPE '\\'
    """
    #'cri', 'cra', 'Debenture', 
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        listado = [x[0] for x in results]
        return listado
    except pyodbc.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Função para puxar os preços do Comdinheiro
def fetch_data(tickers):
    listas = [tickers[i:i+300] for i in range(0, len(tickers), 300)]
    all_ativos = []
    
    for tickers in listas:
        st.write(tickers)
        str_ticker_cmd = '%2B'.join(tickers)
        url = "https://www.comdinheiro.com.br/Clientes/API/EndPoint001.php"
        querystring = {"code":"import_data"}
        
        data_menos_um = date.strftime(data_selection_um, "%d-%m-%Y")
        data_formatda_nova = date.strftime(data_formatada, "%d-%m-%Y")
        
        data_menos_um = "".join(str(dataO) for dataO in data_menos_um).strip()

        st.write(data_menos_um)
        
        st.write(f"data 1: {data_menos_um}, {data_formatda_nova}")
        
        payload = (
            "username=adminconcepta rrodrigues.concepta&password=rrodrigues.concepta&URL=HistoricoCotacao002.php%3F%26x%3D"
            + str_ticker_cmd
            + "%26data_ini%3D" + data_menos_um 
            + "%26data_fim%3D" + data_formatda_nova
            + "%26pagina%3D1%26d%3DMOEDA_ORIGINAL%26g%3D0%26m%3D0%26info_desejada%3Dpreco%26retorno%3Ddiscreto%26tipo_data%3Ddu_br%26tipo_ajuste%3Dtodosajustes%26num_casas%3D2%26enviar_email%3D0%26ordem_legenda%3D1%26cabecalho_excel%3Dmodo2%26classes_ativos%3Dz1ci99jj7473%26ordem_data%3D0%26rent_acum%3Drent_acum%26minY%3D%26maxY%3D%26deltaY%3D%26preco_nd_ant%3D0%26base_num_indice%3D100%26flag_num_indice%3D0%26eixo_x%3DData%26startX%3D0%26max_list_size%3D20%26line_width%3D2%26titulo_grafico%3D%26legenda_eixoy%3D%26tipo_grafico%3Dline%26script%3D%26tooltip%3Dunica&format=json"
        )
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, data=payload, headers=headers, params=querystring)
        
        st.write(response.text)
                
        get_response = requests.get("https://" + response.text.strip())
        
        st.write(type(get_response))
        
        tabela = json.loads(get_response.content.decode('latin-1'))
        
        ativos_nd = tabela['resposta']['tab-p1']['linha'][1]
        
        dados = [(k,v) for k, v in ativos_nd.items() if k!= "data"]
        
        df = pd.DataFrame(dados, columns=["Ticker", "Valor"])
        
        df["Valor"] = df["Valor"].str.replace(",", ".").astype(str)
        
        st.dataframe(df)
        
# Configuração da interface do Streamlit
st.title("Consulta de Ativos")
st.header("Ativos não importados")
opcao_selecionada = st.selectbox(
    "Selecione a opção:",
    ("onshore", "offshore")
)

# Obtém os tickers
data_selection = st.date_input("selecione uma data ", value=date.today())
data_selection_um = data_selection - timedelta(days=1)
data_formatada = date.strftime(data_selection, "%Y-%m-%d")
data_selection_um = date.strftime(data_selection_um, "%Y-%m-%d")

st.write(f"data 1: {data_selection_um}")
st.write(f"data 1: {data_formatada}")
tickers = get_tickers()


if tickers:
    st.success(f"{len(tickers)} tickers encontrados.")
    st.write("Deseja verificar importação de qual data?")


    if st.button("Pesquisar"):
        ativos = fetch_data(tickers)
        st.write('O botão foi clicado!')

    st.write("Ativos recuperados:")
    st.write(ativos)
else:
    st.warning("Nenhum ticker encontrado.")
