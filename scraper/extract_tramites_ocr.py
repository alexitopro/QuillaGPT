from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import json

driver = webdriver.Firefox()

#open the website
driver.get("https://estudiante.pucp.edu.pe/tramites-y-certificaciones/tramites-academicos/?dirigido_a%5B%5D=Estudiantes&unidad%5B%5D=Facultad+de+Ciencias+e+Ingenier%C3%ADa")

#obtener el page source
html = driver.page_source

#guardar los page source de todos los links de tramites
#realizar acciones en el webpage
soup = BeautifulSoup(html, 'html.parser')

#arreglo donde guardare la data de los tramites
tramites_data = []

#recorrer cada pagina de tramites
paginas = soup.find('ul', class_ = 'pagination').find_all('li')
for pagina in paginas:
    link = pagina.find('a')
    if link.text != '1':
        driver.get(link['href'])
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

    #encontrar los divs que tengan los tramites
    tramites = soup.find_all('div', class_ = 'cursos-item')

    #iterar sobre los tramites
    for tramite in tramites:
        #obtener el nombre del tramite
        nombre_tramite = tramite.find('a').text
        #obtener el link del tramite
        link_tramite = tramite.find('a')['href']
        #abrir el link del tramite
        driver.get(link_tramite)
        #obtener el page source del tramite
        html_tramite = driver.page_source
        #realizar acciones en el webpage del tramite
        soup_tramite = BeautifulSoup(html_tramite, 'html.parser')
        #obtener el p que tenga la clase text center
        quote = soup_tramite.find('p', class_ = 'text-center')
        #obtener informacion del tramite como tal
        info_tramite = soup_tramite.find('div', class_ = 'formato')

        info_tramite_text = ''
        info_tramite_text = info_tramite.text.strip()

        for link in info_tramite.find_all('a'):
            if "aquí" in link.text.lower():
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
            'fecha de extracción': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tramites_data.append(tramite_data)

#guardar los datos en un archivo JSON
with open('../data/tramites_data_ocr.json', 'w', encoding='utf-8') as json_file:
    json.dump(tramites_data, json_file, ensure_ascii=False, indent=4)

#cerrar el driver
driver.quit()