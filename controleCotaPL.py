import requests
import json
import pyodbc
from datetime import datetime
import time

class DataRetriever:
    def __init__(self, username, password, db_conn_str):
        self.username = username
        self.password = password
        self.db_conn_str = db_conn_str
        self.agrupamento = []
        self.grupo_completo = ""
        self.conn = None
        self.cursor = None

    def connect_db(self):
        try:
            self.conn = pyodbc.connect(self.db_conn_str)
            self.cursor = self.conn.cursor()
        except pyodbc.Error as e:
            print("Erro de conexão: ", e)

    def fetch_agrupamento(self):
        try:
            query = f"""
            SELECT DISTINCT 
                cod AS unico
            FROM 
                [dbo].[clientes] WHERE jurisdicao = 'onshore'
            UNION
            SELECT DISTINCT 
                agrupamento AS unico
            FROM 
                [dbo].[clientes] WHERE jurisdicao = 'onshore'
            ORDER BY 
                unico ASC;
            """
            self.cursor.execute(query)
            for item in self.cursor:
                self.agrupamento.append(item[0])
        except pyodbc.Error as e:
            print("Erro de execução: ", e)

    def prepare_grupo_completo(self):
        ext = 'ext_'
        cota = '_cota'
        pl = '_pl'
        for item in self.agrupamento[:len(self.agrupamento)//2]:
            self.grupo_completo += f"{ext}{item}{cota}%2b{ext}{item}{pl}%2b"

    def obter_dados(self, data_ini, data_fim):
        url = "https://www.comdinheiro.com.br/Clientes/API/EndPoint001.php"
        querystring = {"code": "import_data"}
        payload = (f"username={self.username}&password={self.password}&URL=HistoricoCotacao002.php%3F%26x%3D"
                   f"{self.grupo_completo[:-3]}%26data_ini%3D{data_ini}%26data_fim%3D{data_fim}"
                   "%26pagina%3D1%26d%3DMOEDA_ORIGINAL%26g%3D0%26m%3D0%26info_desejada%3Dpreco"
                   "%26retorno%3Ddiscreto%26tipo_data%3Ddu_br%26tipo_ajuste%3Dtodosajustes"
                   "%26num_casas%3D8%26enviar_email%3D0%26ordem_legenda%3D1%26cabecalho_excel%3Dmodo1"
                   "%26classes_ativos%3Dz1ci99jj7473%26ordem_data%3D0%26rent_acum%3Drent_acum"
                   "%26minY%3D%26maxY%3D%26deltaY%3D%26preco_nd_ant%3D1%26base_num_indice%3D100"
                   "%26flag_num_indice%3D0%26eixo_x%3DData%26startX%3D0%26max_list_size%3D20"
                   "%26line_width%3D2%26titulo_grafico%3D%26legenda_eixoy%3D%26tipo_grafico%3Dline"
                   "%26script%3D%26tooltip%3Dunica&format=json")
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, data=payload, headers=headers, params=querystring)
        return response.text
        
    def process_response(self, resultado):
        cart_request = requests.get("https://" + resultado)
        posicoes = json.loads(cart_request.content.decode('latin-1'))
        posicoes = posicoes['resposta']['tab-p1']['linha']

        for data in posicoes:
            cotas = {}
            pls = {}
            data_ref = data['data']
            for chave, valor in data.items():
                if chave.endswith("_cota"):
                    cliente = chave.split("_")[1]
                    valor_cota = 0.0 if valor == "nd" else round(float(valor.replace(",", ".")), 8)
                    cotas[cliente] = valor_cota
                if chave.endswith("_pl"):
                    cliente = chave.split("_")[1]
                    valor_pl = 0.0 if valor == "nd" else round(float(valor.replace(",", ".")), 8)
                    pls[cliente] = valor_pl

                    if cliente[2] == '1':
                        jurisdicao = 0
                    else: 
                        jurisdicao = 1
                        
                    data_ref_formatada = datetime.strptime(data_ref, "%d/%m/%Y").strftime("%Y-%m-%d")
                    self.save_to_db(data_ref_formatada, cliente, valor_cota, valor_pl, jurisdicao)

    def save_to_db(self, data_ref_formatada, cliente, valor_cota, valor_pl, jurisdicao):
        try:
            sql = """
               INSERT INTO dbo.historicoCota (data_ref, clientes, valor_cota, valor_pl, jurisdicao)
               VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(sql, data_ref_formatada, cliente, valor_cota, valor_pl, jurisdicao)
            self.conn.commit()
        except pyodbc.Error as e:
            print("Erro ao salvar no banco de dados: ", e)

    def close_db(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    ini_time = time.time()
    print(f'Começou {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    username = "adminconcepta rrodrigues.concepta"
    password = "rrodrigues.concepta"
    db_conn_str = ('Driver={SQL Server};'
                   'Server=tcp:oikoswm.database.windows.net,1433;'
                   'Database=Oikos;'
                   'Uid=oikosroot;'
                   'Pwd=AgpPs@7$2qL0?&of;'
                   'Encrypt=yes;'
                   'TrustServerCertificate=no;'
                   'Connection Timeout=60;'
                   'Schema=dbo')
    
    data_ini = "31/07/2024"
    data_fim = "23/08/2024"
    retriever = DataRetriever(username, password, db_conn_str)
    retriever.connect_db()
    retriever.fetch_agrupamento()
    retriever.prepare_grupo_completo()
    resultado = retriever.obter_dados(data_ini, data_fim)
    retriever.process_response(resultado)
    retriever.close_db()

    fim_time = time.time()
    tempo_exec = fim_time - ini_time
    
    print(f"Tempo de execução: {tempo_exec:.2f} segundos")
    print(f'Terminou {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
if __name__ == "__main__":
    main()
