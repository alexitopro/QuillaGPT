from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import json

driver = webdriver.Firefox()

#open the website
driver.get("https://sites.google.com/pucp.edu.pe/fci-pucp/estudiantes/atenci%C3%B3n-de-tr%C3%A1mites-acad%C3%A9micos")

#obtener el page source
html = driver.page_source

#guardar los page source de todos los links de tramites
soup = BeautifulSoup(html, 'html.parser')

#arreglo donde guardare la data de los tramites
tramites_data = []

contacto = soup.find('div', class_ = 'hJDwNd-AhqUyc-wNfPc Ft7HRd-AhqUyc-wNfPc purZT-AhqUyc-II5mzb ZcASvf-AhqUyc-II5mzb pSzOP-AhqUyc-wNfPc Ktthjf-AhqUyc-wNfPc JNdkSc SQVYQc yYI8W HQwdzb').find('div', class_ = 'JNdkSc-SmKAyb LkDMRd').find('div', class_ =  'U26fgb L7IXhc htnAL QmpIrf M9Bg4d').find('a')['href']

tramites = soup.find('div', class_ = 'hJDwNd-AhqUyc-OwsYgb Ft7HRd-AhqUyc-OwsYgb purZT-AhqUyc-II5mzb ZcASvf-AhqUyc-II5mzb pSzOP-AhqUyc-qWD73c Ktthjf-AhqUyc-qWD73c JNdkSc SQVYQc yYI8W HQwdzb').find('div', class_ = 'JNdkSc-SmKAyb LkDMRd').find_all('div', 'oKdM2c ZZyype')

for tramite in tramites:
    nombre_tramite = tramite.find('a').find('p').get_text()
    link_tramite = tramite.find('a')['href']
    tramite_data = {
        'nombre': nombre_tramite,
        'link': link_tramite,
        'fecha de extracción': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'contacto': contacto
    }
    tramites_data.append(tramite_data)

#guardar la data en un archivo json
with open('../data/tramites_data_sites.json', 'w', encoding='utf-8') as json_file:
    json.dump(tramites_data, json_file, ensure_ascii=False, indent=4)

#cerrar el driver
driver.quit()