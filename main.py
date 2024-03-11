import pandas as pd
import requests
from bs4 import BeautifulSoup, ResultSet
import re
import logging

url_principal_2024_I = 'https://admision.unmsm.edu.pe/Website20241/index.html'
url_principal_2024_II = 'https://admision.unmsm.edu.pe/Website20242/index.html'

url_principal = url_principal_2024_II

id_proceso = '2024-II'
session = requests.session()


def indexando_hrefs_modalidades(items: ResultSet) -> list:
    data = []

    for item in items:
        data.append((url_principal.replace('index.html', item.find_next('a')['href']),
                     item.find_next('a').text.encode('latin1').decode('utf-8')))

    return data


def indexando_hrefs_carreras(data_modalidad: tuple) -> list:
    hrefs = []

    request = requests.get(data_modalidad[0])
    soup = BeautifulSoup(request.text, 'html.parser')
    items = soup.find('tbody').find_all('tr')

    for item in items:
        href = str(item.find_next('a')['href'].replace('./', ''))
        hrefs.append((re.sub("[ACDEFGHIMNO].html", href, data_modalidad[0]), data_modalidad[1]))

    return hrefs


def data_postulantes(data_carrera: tuple) -> list[list[int | str | float | None]]:
    data = []

    request = requests.get(data_carrera[0])
    soup = BeautifulSoup(request.text, 'html.parser')
    items = soup.find('tbody').find_all('tr')

    for item in items:
        codigo = item.find_next('td')
        nombre_postulante = codigo.find_next('td')
        escuela_profesional = nombre_postulante.find_next('td')
        puntaje_final = escuela_profesional.find_next('td')
        merito = puntaje_final.find_next('td')
        observacion = merito.find_next('td')
        escuela_segunda_opcion = observacion.find_next('td')

        data.append(
            limpieza_data_postulante(
                [codigo.text, nombre_postulante.text, escuela_profesional.text, puntaje_final.text,
                 merito.text, observacion.text, escuela_segunda_opcion.text],
                data_carrera[1])
        )

    return data


def limpieza_data_postulante(data_postulante: list, modalidad: str) -> list:
    codigo = int(data_postulante[0])
    nombre_postulante = data_postulante[1].encode('latin1').decode('utf-8')
    escuela_profesional = data_postulante[2].encode('latin1').decode('utf-8')
    puntaje_final = data_postulante[3]  # float(data_postulante[3]) if data_postulante[3].isnumeric() else 0.0
    merito = int(data_postulante[4]) if data_postulante[4].isnumeric() else None
    observacion = data_postulante[5].replace('\xa0', '')
    escuela_segunda_opcion = data_postulante[6].replace('\xa0', '').encode('latin1').decode('utf-8')

    return [codigo, nombre_postulante, escuela_profesional, puntaje_final, merito, observacion,
            escuela_segunda_opcion, id_proceso, modalidad]


def data_a_csv(data: list, nombre_archivo: str):
    headers = ['Codigo', 'Apellidos y Nombres', 'Escuela Profesional', 'Puntaje Final', 'Merito', 'Observacion',
               'Escuela Segunda Opcion', 'Proceso', 'Modalidad']
    data_df = pd.DataFrame(data, columns=headers)

    data_df.to_csv(nombre_archivo, index=False, encoding='utf-8')
    print("Se completo la operacion de manera exitosa")


def main():
    request = requests.get(url_principal)
    logging.warning("Empezando el script")

    soup = BeautifulSoup(request.text, 'html.parser')
    items = soup.find('tbody').find_all('td')
    hrefs_modalidades = indexando_hrefs_modalidades(items)
    data_carreras = []
    data = []

    for href in hrefs_modalidades:
        data_carreras = data_carreras + indexando_hrefs_carreras(href)

    for dat in data_carreras:
        data = data + data_postulantes(dat)

    data_a_csv(data, '2024-II.csv')


if __name__ == '__main__':
    main()
