from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import json

def extract_tramites_ocr():
    driver = webdriver.Firefox()

    with open('./data/ocr_keyword_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    #abrir la pagina web
    driver.get(config['url'])

    #obtener el page source
    html = driver.page_source

    #guardar los page source de todos los links de tramites
    #realizar acciones en el webpage
    soup = BeautifulSoup(html, 'html.parser')

    #arreglo donde guardare la data de los tramites
    tramites_data = []

    #recorrer cada pagina de tramites
    paginas = soup.find(
        config['selectores']['paginacion']['tipo'], 
        class_ =  config['selectores']['paginacion']['clase']
    ).find_all(config['selectores']['item_pagina']['tipo'])

    for pagina in paginas:
        link = pagina.find(config['selectores']['link_pagina']['tipo'])

        #si el link no es la primera pagina guardarla
        if link.text != '1':
            driver.get(link['href'])
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

        #encontrar los divs que tengan los tramites
        tramites = soup.find_all(
            config['selectores']['contenedor_tramites']['tipo'], 
            class_ = config['selectores']['contenedor_tramites']['clase']
        )

        #iterar sobre los tramites
        for tramite in tramites:
            #obtener el nombre del tramite
            nombre_tramite = tramite.find(config['selectores']['nombre_tramite']['tipo']).text
            #obtener el link del tramite
            link_tramite = tramite.find(config['selectores']['link_tramite']['tipo'])['href']
            #abrir el link del tramite
            driver.get(link_tramite)
            #obtener el page source del tramite
            html_tramite = driver.page_source
            #realizar acciones en el webpage del tramite
            soup_tramite = BeautifulSoup(html_tramite, 'html.parser')
            #obtener el p que tenga la clase text center
            quote = soup_tramite.find(
                config['selectores']['quote']['tipo'], 
                class_ = config['selectores']['quote']['clase']
            )
            #obtener informacion del tramite como tal
            info_tramite = soup_tramite.find(
                config['selectores']['info_tramite']['tipo'], 
                class_ = config['selectores']['info_tramite']['clase']
            )

            info_tramite_text = ''
            info_tramite_text = info_tramite.text.strip()

            for link in info_tramite.find_all('a'):
                if config['selectores']['enlace_aqui']['texto'] in link.text.lower():
                    #reemplaza solo el texto "aquí"por el enlace correspondiente
                    info_tramite_text = info_tramite.get_text()
                    link_text = link.text
                    
                    #reemplaza la palabra "aquí" solo en el contexto de ese enlace
                    info_tramite_text = info_tramite_text.replace(link_text, f"{link_text} ({link['href']})")

                    #elimina el enlace del contenido
                    link.decompose()

            tramite_data = {
                'nombre': nombre_tramite,
                'link': link_tramite,
                'informacion': info_tramite_text,
                'quote': quote.text if quote else '',
                'fuente': 'Portal del estudiante',
                'fecha de extracción': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            tramites_data.append(tramite_data)

    #guardar los datos en un archivo JSON
    with open('./data/tramites_data_ocr.json', 'w', encoding='utf-8') as json_file:
        json.dump(tramites_data, json_file, ensure_ascii=False, indent=4)

    #cerrar el driver
    driver.quit()