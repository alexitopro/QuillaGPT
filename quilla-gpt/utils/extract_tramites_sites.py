from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import json

def extract_tramites_sites():
    driver = webdriver.Firefox()

    with open('./data/sites_keyword_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    #abrir la pagina web
    driver.get(config['url'])

    #obtener el page source
    html = driver.page_source

    #guardar los page source de todos los links de tramites
    soup = BeautifulSoup(html, 'html.parser')

    #arreglo donde guardare la data de los tramites
    tramites_data = []

    contacto = soup.find(
        config['selectores']['contacto']['contenedor']['tipo'], 
        class_ = config['selectores']['contacto']['contenedor']['clase']
    ).find(
        config['selectores']['contacto']['subcontenedor']['tipo'], 
        class_ = config['selectores']['contacto']['subcontenedor']['clase']
    ).find(
        config['selectores']['contacto']['subcontenedor']['tipo'], 
        class_ =  config['selectores']['contacto']['enlace']['clase']
    ).find(config['selectores']['contacto']['enlace']['tipo'])['href']

    tramites = soup.find(
        config['selectores']['tramites']['contenedor']['tipo'], 
        class_ = config['selectores']['tramites']['contenedor']['clase']
    ).find(
        config['selectores']['tramites']['subcontenedor']['tipo'], 
        class_ = config['selectores']['tramites']['subcontenedor']['clase']
    ).find_all(
        config['selectores']['tramites']['item_tramite']['tipo'], 
        config['selectores']['tramites']['item_tramite']['clase']
    )

    for tramite in tramites:
        nombre_tramite = tramite.find(config['selectores']['tramites']['link_tramite']['tipo']).find(config['selectores']['tramites']['nombre_tramite']['tipo']).get_text()
        link_tramite = tramite.find(config['selectores']['tramites']['link_tramite']['tipo'])['href']
        tramite_data = {
            'nombre': nombre_tramite,
            'link': link_tramite,
            'fecha de extracción': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'fuente': 'Google Sites de la S. Académica de la FCI',
            'contacto': contacto
        }
        tramites_data.append(tramite_data)

    #guardar la data en un archivo json
    with open('./data/tramites_data_sites.json', 'w', encoding='utf-8') as json_file:
        json.dump(tramites_data, json_file, ensure_ascii=False, indent=4)

    #cerrar el driver
    driver.quit()