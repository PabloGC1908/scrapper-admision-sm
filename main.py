import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup, ResultSet

url_principal_2024_I = 'https://admision.unmsm.edu.pe/Website20241/index.html'
url_principal_2024_II = 'https://admision.unmsm.edu.pe/Website20242/index.html'
url_principal_simulacro_2025_I = 'https://admision.unmsm.edu.pe/WebsiteSimulacro20251/index.html'
url_principal_2025_I = 'https://admision.unmsm.edu.pe/Website20251/index.html'
url_principal_2025_II_A = 'https://admision.unmsm.edu.pe/Website20252GeneralA/index.html'
url_principal_2025_II = 'https://admision.unmsm.edu.pe/Website20252General/index.html'
url_principal_simulacro_2026_I = 'https://admision.unmsm.edu.pe/Website20261/index.html'

url_principal = url_principal_2025_II

id_proceso = '2025-II_2'
session = requests.session()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def indexando_hrefs_modalidades(items: ResultSet) -> list:
    data = []

    for item in items:
        logger.info(f"Registrando datos de {item.text}")
        data.append((url_principal.replace('index.html', item.find_next('a')['href']),
                     item.find_next('a').text.encode('latin1').decode('utf-8')))

    logger.info(f"Data registrada: {data}")

    return data


def indexando_hrefs_carreras(data_modalidad: tuple) -> list:
    logger.info(f"Data registrada: {data_modalidad}")
    hrefs = []

    request = requests.get(data_modalidad[0])
    soup = BeautifulSoup(request.text, 'html.parser')
    items = soup.find('tbody').find_all('tr')

    for item in items:
        logger.info(f"Registrando datos de {item.text}")
        href = str(item.find_next('a')['href'].replace('./', ''))
        logger.info(f"Href: {href}")

        base_url = data_modalidad[0].rpartition('/')[0]

        item_ = (base_url + '/' + href, data_modalidad[1])
        hrefs.append(item_)
        logger.info(f"Indexando url de carrera: {item_}")

    return hrefs


def data_postulantes(data_carrera: tuple) -> list[list[int | str | float | None]]:
    data = []

    request = requests.get(data_carrera[0])
    soup = BeautifulSoup(request.text, 'html.parser')

    items = soup.find('tbody').find_all('tr')

    for item in items:
        print(item.text)
        codigo = item.find_next('td')
        nombre_postulante = codigo.find_next('td')
        escuela_profesional = nombre_postulante.find_next('td')
        puntaje_final = escuela_profesional.find_next('td')
        merito = puntaje_final.find_next('td')
        observacion = merito.find_next('td')

        datos_postulante = [
            codigo,
            nombre_postulante,
            escuela_profesional,
            puntaje_final,
            merito,
            observacion
        ]

        logger.info(f"Datos postulante: {datos_postulante}")

        data.append(limpieza_data_postulante(datos_postulante, data_carrera[1]))

    return data


def limpieza_data_postulante(data_postulante: list, modalidad: str) -> list:
    codigo = data_postulante[0].text.strip() if data_postulante[0] else None
    nombre_postulante = (data_postulante[1].text.strip().encode('latin1').decode('utf-8')
                         if data_postulante[1] else None)
    escuela_profesional = (data_postulante[2].text.strip().encode('latin1').decode('utf-8')
                           if data_postulante[2] else None)
    puntaje_final = limpiar_puntaje_final(data_postulante[3])
    merito = (int(data_postulante[4].text.strip())
              if data_postulante[4] and data_postulante[4].text.strip().isnumeric()
              else None)
    observacion = (data_postulante[5].text.strip().encode('latin1').decode('utf-8')
                   if data_postulante[5] else None)

    logger.info(f"Alumno limpiado: {[codigo, nombre_postulante, escuela_profesional, puntaje_final, merito, observacion, modalidad]}")

    return [codigo, nombre_postulante, escuela_profesional, puntaje_final, merito, observacion, id_proceso, modalidad]


def limpiar_puntaje_final(data):
    logger.debug(f"Tipo del dato: {type(data)}")
    logger.debug(f"Valor de puntaje final antes de limpiar: {data.text}")

    if not data:
        return None

    if isinstance(data, str):
        return data.replace('\xa0', '').strip()

    if hasattr(data, 'text'):
        data_text = data.text.strip()
        return data_text.replace('\xa0', '') if data_text else None

    return None


def data_a_csv(data: list, nombre_archivo: str):
    headers = ['Codigo', 'Apellidos y Nombres', 'Escuela Profesional', 'Puntaje Final', 'Merito', 'Observacion', 'Proceso', 'Modalidad']
    data_df = pd.DataFrame(data, columns=headers)

    data_df.to_csv(nombre_archivo, index=False, encoding='utf-8')
    logger.info(f"Se registraron los datos en el archivo {nombre_archivo}")


def main():
    request = requests.get(url_principal)
    logger.info("Empezando el script")

    soup = BeautifulSoup(request.text, 'html.parser')
    items = soup.find('tbody').find_all('td')
    hrefs_modalidades = indexando_hrefs_modalidades(items)
    data_carreras = []
    data = []

    for href in hrefs_modalidades:
        logger.info(f"Registrando carreras de modalidad: {href}")
        data_carreras = data_carreras + indexando_hrefs_carreras(href)

    logger.info(f"Data registrada: {data_carreras}")

    for dat in data_carreras:
        data = data + data_postulantes(dat)

    data_a_csv(data, f'{id_proceso}.csv')


if __name__ == '__main__':
    main()
