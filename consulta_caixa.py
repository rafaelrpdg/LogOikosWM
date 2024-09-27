import requests
import locale
import pyperclip


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

url = "https://www.comdinheiro.com.br/Clientes/API/EndPoint001.php"

querystring = {"code":"import_data"}

data = input("Data: ")

while True:
    carteira = input("Carteira: ")
    
    payload = "username=adminconcepta rrodrigues.concepta&password=rrodrigues.concepta&URL=RelatorioGerencialCarteiras001.php%3F%26data_analise%3D"+ data +"%26data_ini%3D%26layout%3D0%26filtro%3DCaixa%26layoutB%3D0%26nome_portfolio%3D"+ carteira +"%26portfolio_editavel%3D%26variaveis%3Dnome_portfolio%2Bcv_alias%2Bsaldo_bruto%26enviar_email%3D0%26ativo%3D%26filtro_IF%3Dtodos%26relat_alias%3D%26num_casas%3D&format=json2"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    
    response = response.json()

    valorbruto = float(str(response['resposta']['tab-p0']['linha']['saldo_bruto']).replace(",","."))
    
    valorformatado = locale.currency(valorbruto, grouping=True)
    
    pyperclip.copy(valorformatado)
        
    print(valorformatado)