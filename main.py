import pandas as pd
import requests
from bs4 import BeautifulSoup, ResultSet

session = requests.session()
url = "https://admision.unmsm.edu.pe/WebsiteExa_20232/A.html"
id_proceso = '2023-II'


def indexando_hrefs(items: ResultSet) -> list:
    hrefs = []

    for item in items:
        href = str(item.find_next('a')['href'].replace('./A', ''))
        hrefs.append(url.replace('.html', href))

    return hrefs


def data_postulantes(href: str) -> list[list[int | str | float | None]]:
    data = []

    request = requests.get(href)
    soup = BeautifulSoup(request.text, 'html.parser')
    items = soup.find('tbody').find_all('tr')

    for item in items:
        codigo = item.find_next('td')
        nombre_postulante_data = codigo.find_next('td')
        escuela_profesional_data = nombre_postulante_data.find_next('td')
        puntaje_final_data = escuela_profesional_data.find_next('td')
        merito_ep = puntaje_final_data.find_next('td')
        ingreso = merito_ep.find_next('td')

        nombre_postulante = nombre_postulante_data.text.encode('latin1').decode('utf-8')
        escuela_profesional = escuela_profesional_data.text.encode('latin1').decode('utf-8')

        if puntaje_final_data.text.isnumeric():
            puntaje_final = float(puntaje_final_data.text)
        else:
            puntaje_final = 0.00

        if merito_ep.text.isnumeric():
            merito_ep = int(merito_ep.text)
        else:
            merito_ep = None

        ingreso = ingreso.text.replace('\xa0', '')

        data.append([int(codigo.text), nombre_postulante, escuela_profesional, puntaje_final, merito_ep, ingreso,
                     id_proceso])

    return data


def data_a_csv(data: list):
    headers = ['Codigo', 'Apellidos y Nombres', 'Escuela Profesional', 'Puntaje Final', 'Merito', 'Observacion',
               'Proceso']
    data_df = pd.DataFrame(data, columns=headers)

    data_df.to_csv('2023_II.csv', index=False, encoding='utf-8')


def main():
    request = requests.get(url)

    soup = BeautifulSoup(request.text, 'html.parser')

    items = soup.find('tbody').find_all('td')
    hrefs = indexando_hrefs(items)
    data = []

    for href in hrefs:
        data = data + data_postulantes(href)

    data_a_csv(data)


if __name__ == '__main__':
    main()
