from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import json

driver = webdriver.Firefox()

#open the website
driver.get("https://facultad-ciencias-ingenieria.pucp.edu.pe/estudiantes/tramites-academicos-y-administrativos/")

#obtener el page source
html = driver.page_source

#guardar los page source de todos los links de tramites
soup = BeautifulSoup(html, 'html.parser')

#arreglo donde guardare la data de los tramites
tramites_data = []

tramites_source = soup.find('div', class_ = 's-m-b-4 w-richtext')

tramites = tramites_source.find('ul').find_all('li', recursive=False)
for tramite in tramites:
    nombre_tramite = tramite.find('strong').get_text()
    if (nombre_tramite != 'Otros trámites en la FCI'):
        link_tramite = tramite.find('a')['href'] if tramite.find('a').find('strong') else ''
        consideraciones_adicionales = ''
        if tramite.find('ul'):
            consideraciones_adicionales = tramite.find('ul').get_text()

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
        nombre_tramite = tramite.find('strong').get_text()
        link_tramite = tramite.find('a')['href'] if tramite.find('a').find('strong') or tramite.find('strong').find('a') else ''
        consideraciones_adicionales = ''
        if tramite.find('ul'):
            consideraciones_adicionales = tramite.find('ul').get_text()

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
with open('../data/tramites_data_fci.json', 'w', encoding='utf-8') as json_file:
    json.dump(tramites_data, json_file, ensure_ascii=False, indent=4)

#cerrar el driver
driver.quit()