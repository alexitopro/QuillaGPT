from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import json

def extract_tramites_fci():
    driver = webdriver.Firefox()

    with open('./data/fci_keyword_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    #abrir la pagina web
    driver.get(config['url'])

    #obtener el page source
    html = driver.page_source

    #guardar los page source de todos los links de tramites
    soup = BeautifulSoup(html, 'html.parser')

    #arreglo donde guardare la data de los tramites
    tramites_data = []

    tramites_source = soup.find(
        config['selectores']['contenedor_tramites']['tipo'], 
        class_ = config['selectores']['contenedor_tramites']['clase']
    )

    tramites = tramites_source.find(config['selectores']['lista_tramites']['tipo']).find_all(config['selectores']['item_tramite']['tipo'], recursive=False)

    for tramite in tramites:
        nombre_tramite = tramite.find(config['selectores']['nombre_tramite']['tipo']).get_text()
        
        if (nombre_tramite != config['keywords']['excluir']):
            link_tramite = tramite.find(config['selectores']['link_tramite']['tipo'])['href'] if tramite.find(config['selectores']['link_tramite']['tipo']).find(config['selectores']['nombre_tramite']['tipo']) else ''
            
            consideraciones_adicionales = ''
            if tramite.find(config['selectores']['consideraciones_adicionales']['tipo']):
                consideraciones_adicionales = tramite.find(config['selectores']['consideraciones_adicionales']['tipo']).get_text()

            tramite_data = {
                'nombre': nombre_tramite,
                'link': link_tramite,
                'informacion': consideraciones_adicionales,
                'fecha de extracción': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            tramites_data.append(tramite_data)

    tramites = tramites_source.find_all('p')
    for tramite in tramites:
        if tramite.find('a'):
            nombre_tramite = tramite.find(config['selectores']['nombre_tramite']['tipo']).get_text()

            link_tramite = tramite.find(config['selectores']['link_tramite']['tipo'])['href'] if tramite.find(config['selectores']['link_tramite']['tipo']).find(config['selectores']['nombre_tramite']['tipo']) or tramite.find(config['selectores']['nombre_tramite']['tipo']).find(config['selectores']['link_tramite']['tipo']) else config['url']

            consideraciones_adicionales = ''
            if tramite.find(config['selectores']['consideraciones_adicionales']['tipo']):
                consideraciones_adicionales = tramite.find(config['selectores']['consideraciones_adicionales']['tipo']).get_text()

            tramite_data = {
                'nombre': nombre_tramite,
                'link': link_tramite,
                'informacion': consideraciones_adicionales,
                'fecha de extracción': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if (not link_tramite and not consideraciones_adicionales):
                continue
            tramites_data.append(tramite_data)

    #guardar la data en un archivo json
    with open('./data/tramites_data_fci.json', 'w', encoding='utf-8') as json_file:
        json.dump(tramites_data, json_file, ensure_ascii=False, indent=4)

    #cerrar el driver
    driver.quit()