from selenium import webdriver

path_to_driver = 'caminho/para/o/driver'

# Inicializa o driver do navegador
driver = webdriver.Chrome(executable_path=path_to_driver)

# Abre uma página web
driver.get('http://www.google.com')

# Fecha o navegador
driver.quit()
