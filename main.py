import pandas as pd
import requests
from bs4 import BeautifulSoup, ResultSet
import re
import logging

url_principal_2024_I = 'https://admision.unmsm.edu.pe/Website20241/index.html'
url_principal_2024_II = 'https://admision.unmsm.edu.pe/Website20242/index.html'
url_principal_simulacro_2025_I = 'https://admision.unmsm.edu.pe/WebsiteSimulacro20251/index.html'

url_principal = url_principal_simulacro_2025_I

id_proceso = 'S-2025-I'
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

    items = soup.find('tbody').find_all('td')

    for i in range(0, len(items), 7):
        sede = items[i].text.strip()
        codigo = items[i + 1].text.strip()
        nombre_postulante = items[i + 2].text.strip()
        escuela_profesional = items[i + 3].text.strip()
        puntaje_final = items[i + 4].text.strip()
        merito = items[i + 5].text.strip()
        observacion = items[i + 6].text.strip()

        datos_postulante = [
            sede,
            codigo,
            nombre_postulante,
            escuela_profesional,
            puntaje_final,
            merito,
            observacion
        ]

        logger.info(f"Datos postulante: {datos_postulante}")

        data.append(
            limpieza_data_postulante(datos_postulante, data_carrera[1])
        )

    return data


def limpieza_data_postulante(data_postulante: list, modalidad: str) -> list:
    sede = data_postulante[0].replace('\xa0', '').encode('latin1').decode('utf-8')
    codigo = int(data_postulante[1])
    nombre_postulante = data_postulante[2].encode('latin1').decode('utf-8')
    escuela_profesional = data_postulante[3].encode('latin1').decode('utf-8')
    puntaje_final = limpiar_puntaje_final(data_postulante[4])
    merito = int(data_postulante[5]) if data_postulante[5].isnumeric() else None
    observacion = data_postulante[6].replace('\xa0', '').encode('latin1').decode('utf-8')
    logger.info(f"Alumno limpiado: {[codigo, nombre_postulante, escuela_profesional, puntaje_final, merito, observacion, id_proceso, modalidad]}")

    return [sede, codigo, nombre_postulante, escuela_profesional, puntaje_final, merito, observacion, id_proceso, modalidad]


def limpiar_puntaje_final(data: str):
    if '\xa0' in data:
        return data.replace('\xa0', '')

    if 'Art' in data:
        return data.encode(encoding='utf-8', errors='ignore').decode('utf-8')

    return data


def data_a_csv(data: list, nombre_archivo: str):
    headers = ['Sede', 'Codigo', 'Apellidos y Nombres', 'Escuela Profesional', 'Puntaje Final', 'Merito', 'Observacion', 'Proceso', 'Modalidad']
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

    data_a_csv(data, 'S-2025-I.csv')


if __name__ == '__main__':
    main()
