# Scraper de Datos de Admisión UNMSM

Este proyecto es un script en Python diseñado para recopilar datos de postulantes del sitio web de admisión de la Universidad Nacional Mayor de San Marcos (UNMSM). El script navega por las modalidades, programas y lista los datos de los postulantes, guardándolos en un archivo CSV para su análisis posterior.

## Características

- Extracción de datos desde diferentes procesos de admisión (2024-I, 2024-II, 2025-I, simulacros, etc.).
- Limpieza y formato de los datos extraídos.
- Registro de las siguientes informaciones para cada postulante:
  - Código
  - Nombre
  - Escuela Profesional
  - Puntaje Final
  - Mérito
  - Observaciones
  - Proceso de Admisión
  - Modalidad
- Generación de un archivo CSV con los datos recopilados.

## Requisitos

### Dependencias de Python
- Python 3.8 o superior
- `pandas`
- `requests`
- `beautifulsoup4`

### Instalación de dependencias
Usa el archivo `requirements.txt` para instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

1. Clona este repositorio
2. Configura el proceso de admisión que deseas scrapear en la variable url_principal (por defecto, está configurado para el proceso 2025-I).
3. Ejecuta el script:
```bash
python main.py
```
4. El archivo generado se guardara con el nombre del proceso o el que tu gustes, para eso esta el metodo `data_a_csv(data, '2025-I.csv')`

> [!WARNING] 
> Puede que en algunos procesos de admision ya no se puedan scrapear debido a que se dio de baja la pagina, en todo caso, se tiene el csv en crudo con los datos ya scrapeados

## Logs
El script utiliza el módulo `logging` para registrar información de depuración y errores. Los mensajes incluyen detalles sobre el progreso del script y errores potenciales.

## Estructura del csv
La estructura de la data en el csv varia dependiendo del proceso de admision, por lo que los distintos csvs de las distintas modalidades pueden verse con distintos encabezados, en el caso del ultimo proceso (2025-I), el encabezado se veria asi:

| Codigo  | Apellidos y Nombres | Escuela Profesional | Puntaje Final | Merito | Observacion | Proceso | Modalidad |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
## Contribuciones
Si llega a fallar en algun momento (que siempre se tiene que modificar algo cada vez que sale un nuevo proceso de admision) o si tienes una mejora de este codigo, crea un issue o un pull request

