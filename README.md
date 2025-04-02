# Proyecto de Tipología y Ciclo de Vida de los Datos

## Integrantes del Grupo
- Alejandro Pardo Camacho
- Santiago Arranz Orlandi

## Archivos en el Repositorio

- **README.md**: Este archivo que describe el proyecto y su estructura.
- **requirements.txt**: Archivo que contiene las dependencias necesarias para ejecutar el proyecto.
- **/utils.py**: contiene todas las funciones necesarias para raspar información de películas en el portal JustWatch.
- **/dataset**: Contiene el dataset resultante en formato CSV.

## Uso del Código

Para ejecutar el código, asegúrese de tener las dependencias instaladas. Puede instalar las dependencias ejecutando:

```bash
pip install -r requirements.txt
```

La función principal es jw_movies y se encuentra en utils.py, que se encarga de realizar el scraping en el portal JustWatch. Esta función obtiene la información de las películas de un año determinado y admite los siguientes parámetros:
- year (obligatorio):
Indica el año de lanzamiento de las películas a raspar. Por ejemplo, 2020.
- Extractor (opcional, por defecto True):
Si se establece como True, la función extrae información detallada de cada película (incluyendo título, año, plataformas de suscripción, valoraciones en JustWatch, IMDb y Rotten Tomatoes, géneros, duración, clasificación por edades, países de producción e imagen del póster) y devuelve un DataFrame de Pandas, además de generar un archivo CSV con el nombre del año correspondiente.
Si se establece como False, la función únicamente devuelve una lista única de las URLs de las películas encontradas para el año especificado.

## Ejemplos de Uso
- Obtener solo la lista de URLs de las películas de un año (por ejemplo, 1915):

```bash
from utils import jw_movies
movie_list_1915 = jw_movies(1915, Extractor=False)
print(movie_list_1915)
```
Salida esperada:

Starting movie list (1915) scraping...
Movies found: 3
['/es/pelicula/carmen-1915', '/es/pelicula/the-cheat', '/es/pelicula/el-nacimiento-de-una-nacion']

- Obtener la información completa de las películas y generar un archivo CSV:
```bash
from utils import jw_movies
movie_info_1920 = jw_movies(1920)  # Por defecto, Extractor=True
print(movie_info_1920.head())
```
Salida esperada:
Información extraída en "1915.csv"

## Consideraciones Adicionales
- Tiempo de Ejecución:
El proceso de scraping puede tardar varios minutos (o incluso horas) dependiendo de la cantidad de películas a procesar y de las pausas implementadas para evitar sobrecargar el servidor.

- Uso Responsable:
Se recomienda ejecutar el script en rangos de años limitados para evitar sobrecargar el portal web de JustWatch. En caso de querer raspar información de varios años consecutivos, es aconsejable incluir pausas prolongadas entre cada ejecución.
