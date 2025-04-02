# Extracción del título y año de la película
def jw_extract_title_year(soup):

    # Importar librerías
    from bs4 import BeautifulSoup as bs

    # Extracción título y año
    title_year = soup.find("h1", class_="title-detail-hero__details__title") # Elemento contenedor de ambos
    if title_year:
        title_text = title_year.find(string=True, recursive=False) # Texto de título
        if title_text:
            tit = title_text.strip()
        else:
            tit = "NA"
        year_tag = title_year.find("span", class_="release-year") # Elemento contenedor del año
        if year_tag:
            ye = year_tag.text.strip() # Texto de año
        else:
            ye = "NA"
        return tit, ye
    else:
        return "NA", "NA"

#########################################

# Extracción de las plataformas donde la película está disponible bajo suscripción
def jw_extract_platforms(soup):

    # Importar librerías
    from bs4 import BeautifulSoup as bs

    # Extraemos las plataformas de streaming
    stream = []
    offers_section = soup.find("div", class_="buybox buybox-selector") # Elemento contenedor de ofertas
    if offers_section:
        offers = offers_section.find_all("span", class_="offer-container") # Lista de ofertas
        for offer in offers:
            if offer.find("p", class_="offer__label__free-trial"): # Suscripción con prueba gratuita
                stream.append(offer.find("img")['alt'].strip())
            if offer.find("p", class_="offer__label__text"): 
                if offer.find("p", class_="offer__label__text").text == "Suscripción": # Suscripción estándar
                    stream.append(offer.find("img")['alt'].strip())
        if not stream:
                    stream.append(["NA"]) # Si no hay ofertas de suscripción
        return stream
    else:
        return ["NA"]

#########################################

# Extracción de las valoraciones de JustWatch, IMDb y Rotten Tomatoes
def jw_extract_ratings(soup):

    # Importar libreríoas
    from bs4 import BeautifulSoup as bs
    import pandas as pd

    # Extracción de las puntuaciones de JustWatch, IMDb y Rotten Tomatoes
    jw_score = []
    jw_ratings = []
    imdb_score = []
    imdb_ratings = []
    rt_score = []

    areRatings = soup.find('h3', class_='poster-detail-infos__subheading', string='Calificación') # Elemento contenedor de las valoraciones
    if areRatings:
        ratingPlatforms = areRatings.find_next_sibling('div', class_='poster-detail-infos__value').find_all('div', class_="jw-scoring-listing__rating")
        for ratingPlatform in ratingPlatforms: # Detección y asignación de las valoraciones independientemente del orden
            if (ratingPlatform.find('img')['alt'] == "JustWatch Rating"):
                try:
                    jw_score, jw_ratings = ratingPlatform.find('div').text.split()
                except Exception:
                    jw_score = ratingPlatform.find('div').text
                    jw_ratings = "NA"
            elif (ratingPlatform.find('img')['alt'] == "IMDB"):
                try:
                    imdb_score, imdb_ratings = ratingPlatform.find('div').text.split()
                except Exception:
                    imdb_score = ratingPlatform.find('div').text
                    imdb_ratings = "NA"
            elif (ratingPlatform.find('img')['alt'] == "ROTTEN TOMATOES"):
                    rt_score = ratingPlatform.find('div').text
        # Asignación si no existe valoración
        if not jw_score: jw_score = "NA"
        if not jw_ratings: jw_ratings = "NA"
        if not imdb_score: imdb_score = "NA"
        if not imdb_ratings: imdb_ratings = "NA"
        if not rt_score: rt_score = "NA"
    else:
        jw_score = "NA"
        jw_ratings = "NA"
        imdb_score = "NA"
        imdb_ratings = "NA"
        rt_score = "NA"
    return pd.DataFrame({
        "jw_score": jw_score,
        "jw_ratings": jw_ratings,
        "imdb_score": imdb_score,
        "imdb_ratings": imdb_ratings,
        "rt_score": rt_score
    }, index=[0])

#########################################

# Extracción de la información de otros datos de la película
def jw_extract_others(soup, element):

    # Importación de librerías
    from bs4 import BeautifulSoup as bs

    # Extracción del elemento
    isElement = soup.find('h3', class_='poster-detail-infos__subheading', string=element)
    if isElement:
        return isElement.find_next_sibling('div', class_='poster-detail-infos__value').text.strip()
    else:
        return "NA"

#########################################

# Extracción de la imagen del póster de la película
def jw_extract_img(soup):

    # Importación de librerías
    from PIL import Image
    import numpy as np
    import urllib.request
    import json
    import re

    # Extracción de la imagen del póster
    img_tag = soup.find('img', {"data-src": re.compile(r"https://images\.justwatch\.com/poster/.*")}) # Búsqueda del elemento mediante regexp
    if img_tag:
        img_url = img_tag["data-src"]
        try:
            img_response = urllib.request.urlopen(img_url) # Petición al servidor
            img = Image.open(img_response)
            img_array = np.array(img) # Conversión a array
            img_json = json.dumps(img_array.tolist()) # Conversión a JSON (para almacenamiento)
            return img_json
        except Exception:
            return "NA"
    else:
        return "NA"

#########################################

# Extracción de la información de cada película
def jw_extractor(movie_title_list):

    # Importación de librerías
    from bs4 import BeautifulSoup as bs
    from tqdm import tqdm
    from utils import jw_extract_title_year, jw_extract_platforms, jw_extract_ratings, jw_extract_img, jw_extract_others
    import pandas as pd
    import requests
    import time
    import random

    # Inicialización de listas para almacenar la información
    title = []
    year = []
    platforms = []
    jw_score = []
    jw_ratings = []
    imdb_score = []
    imdb_ratings = []
    rt_score = []
    genres = []
    duration = []
    ageRating = []
    countries = []
    poster_image = []

    # User-agent para que la solicitud parezca provenir de un navegador real y evitar bloqueos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    # Iteración sobre la lista de títulos (enlaces)
    for movie in tqdm(movie_title_list, desc="Extracting movie info:"):
        url = f"https://www.justwatch.com{movie}"
        response = requests.get(url, headers=headers)
        soup = bs(response.text, "lxml")

        # Extracción de título y año
        tit, ye = jw_extract_title_year(soup)
        title.append(tit)
        year.append(ye)

        # Extracción de las plataformas de streaming
        platforms.append(jw_extract_platforms(soup))

        # Extracción de las puntuaciones de JustWatch, IMDb y Rotten Tomatoes
        ratings = jw_extract_ratings(soup)
        jw_score.append(ratings.jw_score[0])
        jw_ratings.append(ratings.jw_ratings[0])
        imdb_score.append(ratings.imdb_score[0])
        imdb_ratings.append(ratings.imdb_ratings[0])
        rt_score.append(ratings.rt_score[0])

        # Extracción de los géneros de la película
        genres.append(jw_extract_others(soup, 'Géneros'))

        # Extracción de la duración de la película
        duration.append(jw_extract_others(soup, 'Duración'))

        # Extracción de la clasificación por edades
        ageRating.append(jw_extract_others(soup, 'Clasificación por edades'))
                         
        # Extracción de los países de producción
        countries.append(jw_extract_others(soup, 'País de producción'))

        # Extracción de la imagen del póster
        poster_image.append(jw_extract_img(soup))
                         
        # Espera pseudoaleatoria para no sobrecargar el servidor
        time.sleep(random.uniform(0.3, 1.3))

    # Se devuelve un diccionario con toda la información extraída
    return {
        "title": title,
        "year": year,
        "platforms": platforms,
        "jw_score": jw_score,
        "jw_ratings": jw_ratings,
        "imdb_score": imdb_score,
        "imdb_ratings": imdb_ratings,
        "rt_score": rt_score,
        "genres": genres,
        "duration": duration,
        "ageRating": ageRating,
        "countries": countries,
        "poster_image": poster_image
    }

#########################################

# Gestión del scroll infinito y extracción del html
def jw_scroll(driver):
    
    # Importación de librerías
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    import time
    
    # Realizar scroll hasta el final de la página para cargar contenido
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 3).until(
                lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
            )
            new_height = driver.execute_script("return document.body.scrollHeight")
            last_height = new_height
        # Cuando no se carga más se pasa al siguiente sistema: realizar scroll hacia arriba y hacia abajo para cargar todos los títulos.
        except Exception:
            try:
                iteration_count = 0
                while iteration_count < 15: # Se limita para evitar que cargue infinitamente
                    for _ in range(5):
                        driver.execute_script("window.scrollBy(0, -400);")
                        time.sleep(0.5)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    WebDriverWait(driver, 3).until(
                        lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
                    )
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    iteration_count += 1
            except Exception:
                break

    # Devuelve el html de la página
    return driver.page_source

#########################################

# Obtención del listado de películas
def jw_movies(year, Extractor=True):

    # Importación de librerías
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup as bs
    from utils import jw_scroll, jw_extractor
    import chromedriver_autoinstaller
    import pandas as pd
    import re

    # Lista vacía a devolver
    movie_title_list = []
    
    # User-agent para que la solicitud parezca provenir de un navegador real y evitar bloqueos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    # Configuración del navegador para segundo plano
    options = Options()
    options.add_argument("--headless=new")  # Nueva versión de headless mode
    options.add_argument("--disable-gpu")  # Desactiva el uso de GPU
    options.add_argument("--no-sandbox")  # Evita problemas en servidores
    options.add_argument("--disable-dev-shm-usage")  # Evita errores en entornos con poca memoria compartida
    options.add_argument("--blink-settings=imagesEnabled=false")  # No carga imágenes para optimizar
    options.add_argument("--disable-extensions")  # Desactiva extensiones innecesarias
    options.add_argument("--disable-infobars")  # Evita que muestre avisos de automatización
    options.add_argument("--mute-audio")  # Silencia cualquier posible sonido

    # Apertura del driver con el año especificado
    service = Service()  # Se detecta automáticamente el ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    url = f"https://www.justwatch.com/es/peliculas?providers=atp,dnp,fil,flx,mp9,mvs,mxx,nfa,nfx,prv,sst,atr,mte&release_year_from={year}&release_year_until={year}"
    driver.get(url)

    # Aceptación de las cookies (si aparecen)
    cookie_elements = driver.find_elements(By.CSS_SELECTOR, "#usercentrics-root")
    if cookie_elements:
        try:
            # Acceder al shadow root y buscar el botón para aceptar cookies
            shadow_root = driver.execute_script("return arguments[0].shadowRoot", cookie_elements[0])
            cookie_button = shadow_root.find_element(By.CSS_SELECTOR, ".sc-dcJsrY.dQaUXI")
            cookie_button.click()
        except Exception as e:
            print("There was an Error when accepting cookies:", e)

    # Información al usuario de que ha empezado el proceso
    print(f"Starting movie list ({year}) scraping...")

    # Detección del número de resultados
    nMov = driver.find_element(By.XPATH, "//div[@class='mx-2 me-2 text-medium']").text
    nMov = int(re.sub(r'\D', '', nMov))

    # Extracción en una única vez
    if nMov < 1900:
        html = jw_scroll(driver) # Scroll y generación del html
        soup = bs(html, 'html.parser')
        movie_titles = soup.find_all('a', class_='title-list-grid__item--link', attrs={'href': True}) # Búsqueda de todos los títulos
        movie_title_list = [movie['href'] for movie in movie_titles] # Almacenamiento en una lista

    # Extracción dividida para garantizar el mayor número posible de resultados
    else:
        genreSplit = ["drm,eur,hst,war,wsn,doc",
                  "ani,cmy,fml,msc,rma,spt",
                  "act,crm,fnt,hrr,scf,trl"]
        for genrePack in genreSplit:
            url = f"https://www.justwatch.com/es/peliculas?genres={genrePack}&providers=atp,dnp,fil,flx,mp9,mvs,mxx,nfa,nfx,prv,sst&release_year_from={year}&release_year_until={year}"
            driver.get(url)

        html = jw_scroll(driver) # Scroll y generación del html
        time.sleep(30)
        soup = bs(html, 'lxml')
        movie_titles = soup.find_all('a', class_='title-list-grid__item--link', attrs={'href': True}) # Búsqueda de todos los títulos
        movie_title_list_partial = [movie['href'] for movie in movie_titles] # Almacenamiento en una lista de la división
        movie_title_list += movie_title_list_partial # Almacenamiento en una lista completa

    # Cierre del driver
    driver.quit()

    # Eliminar duplicados
    movie_title_list_unique = list(set(movie_title_list))
    print("Movies found:", len(movie_title_list_unique))

    # Si Extractor es False, se devuelve únicamente la lista de títulos únicos
    if not Extractor:
        return movie_title_list_unique

    # Si Extractor es True, se continúa con el proceso de extracción
    data = jw_extractor(movie_title_list_unique)

    # Data frame resultado
    df = pd.DataFrame({
        "title": data["title"],
        "year": data["year"],
        "platforms": data["platforms"],
        "jw_score": data["jw_score"],
        "jw_ratings": data["jw_ratings"],
        "imdb_score": data["imdb_score"],
        "imdb_ratings": data["imdb_ratings"],
        "rt_score": data["rt_score"],
        "genres": data["genres"],
        "duration": data["duration"],
        "ageRating": data["ageRating"],
        "countries": data["countries"],
        "poster_image": data["poster_image"]

    })

    # Generación del archivo csv
    csv_file = f"{year}.csv"
    df.to_csv(csv_file, sep=";")

    # Devolución
    print(f'Information extracter in "{year}.csv"')
    return df