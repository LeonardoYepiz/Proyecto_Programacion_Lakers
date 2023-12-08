from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Webscraping manual - Obtención de jugadores
pagina = "https://www.basketball-reference.com/teams/LAL/2023.html"
resultado = requests.get(pagina)
contenido = resultado.text

soup = BeautifulSoup(contenido, "lxml")

titulo = soup.find("h1").get_text(strip=True, separator=" ")
print("El título de la página es el siguiente:", titulo)

informacion = soup.find("div", {"id": "info"}).get_text(strip=True, separator=" ")

informacion_por_renglones = informacion.split('\n')
print("La información de la página principal es la siguiente:")
for linea in informacion_por_renglones:
    print(linea)

jugadores_div = soup.find("div", {"id": "div_roster"})

if jugadores_div:
    tabla = jugadores_div.find("table", {"class": "sortable"})
    if tabla:
        datos_jugadores = []
        filas = tabla.find_all("tr")
        for fila in filas[1:]:
            datos = fila.find_all(["th", "td"])
            jugador = [dato.get_text(strip=True) for dato in datos]
            datos_jugadores.append(jugador)

        columnas = [header.get_text(strip=True) for header in filas[0].find_all("th")]
        data_jugadores_df = pd.DataFrame(datos_jugadores, columns=columnas)
        print("La información de los jugadores es la siguiente:", data_jugadores_df)

# Webscraping automatizado - Obtención de asistentes
s = Service(ChromeDriverManager().install())
opc = Options()
opc.add_argument("--window-size=1020,1200")
navegador = webdriver.Chrome(service=s, options=opc)

# Abre la página
url = "https://www.basketball-reference.com/teams/LAL/2023.html"
navegador.get(url)

# Encuentra la sección de los asistentes del equipo
asistentes_div = navegador.find_element(By.ID, "all_assistant_coaches")

if asistentes_div:
    # Extrae la información de la sección de asistentes
    html = asistentes_div.get_attribute("innerHTML")
    soup_asistentes = BeautifulSoup(html, "html.parser")

    print("La información de los asistentes es la siguiente:")
    # Procesa la información de los asistentes y entrenadores
    data_asistentes = []
    asistentes_rows = soup_asistentes.find_all("tr")
    for row in asistentes_rows:
        columns = row.find_all("td")
        if columns:
            nombre = columns[0].find("a").get_text(strip=True)
            cargo = columns[1].get_text(strip=True)
            data_asistentes.append({"Nombre": nombre, "Cargo": cargo})

    # Crea el DataFrame con la información obtenida de asistentes
    data_asistentes_df = pd.DataFrame(data_asistentes)
    print(data_asistentes_df)  # Imprime el DataFrame de asistentes

# Estadísticas de los jugadores durante la temporada regular

especifico_div = navegador.find_element(By.ID, "div_per_game")

if especifico_div:
    especifico_html = especifico_div.get_attribute("innerHTML")
    soup_especifico = BeautifulSoup(especifico_html, "html.parser")

    # Buscar la tabla de estadísticas
    estadisticas_tabla = soup_especifico.find("table")

    if estadisticas_tabla:
        estadisticas_data = []
        rows = estadisticas_tabla.find_all("tr")
        for row in rows[1:]:
            data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            estadisticas_data.append(data)

        columnas = [header.get_text(strip=True) for header in rows[0].find_all("th")]
        estadisticas_df = pd.DataFrame(estadisticas_data, columns=columnas)
        print("Las estadisticas de los jugadores son las siguientes:\n", estadisticas_df)

        # APORTE MARCELO
    
        # Convierte la columna de puntos a tipo numerico (si aun no lo es)
        estadisticas_df['PTS'] = pd.to_numeric(estadisticas_df['PTS'], errors='coerce')
        
        # Clasifica el DataFrame por la columna de puntos en orden descendente
        estadisticas_df = estadisticas_df.sort_values(by='PTS', ascending=False)
        
         # Imprime el DataFrame clasificado
        print("Clasificación de jugadores por puntos:")
        print(estadisticas_df[['Player', 'PTS']])
        
        # Convierte la columna 'G' a tipo numerico
        estadisticas_df['G'] = pd.to_numeric(estadisticas_df['G'], errors='coerce')
        
        # Convierte la columna 'MP' a tipo numerico si aun no lo es
        estadisticas_df['MP'] = pd.to_numeric(estadisticas_df['MP'], errors='coerce')
        
        # Calcula los minutos jugados por partido solo si 'G' y 'MP' son numericos
        mask_numeric = (pd.notnull(estadisticas_df['G'])) & (pd.notnull(estadisticas_df['MP']))
        estadisticas_df.loc[mask_numeric, 'MinPorPartido'] = estadisticas_df['MP'] / estadisticas_df['G']
        
         # Clasifica el DataFrame por la nueva columna 'MinPorPartido' en orden descendente
        estadisticas_df = estadisticas_df.sort_values(by='MinPorPartido', ascending=False)
        
        # Imprime el DataFrame clasificado
        print("Clasificacion de jugadores por minutos jugados por partido:")
        print(estadisticas_df[['Player', 'MinPorPartido']])
        
        # Convierte la columna de edad a tipo numérico (si aún no lo es)
        estadisticas_df['Age'] = pd.to_numeric(estadisticas_df['Age'], errors='coerce')
        
        # Clasifica el DataFrame por la columna de edad en orden descendente
        estadisticas_df = estadisticas_df.sort_values(by='Age', ascending=False)
        
        # Imprime el DataFrame clasificado
        print("Clasificación de jugadores por edad:")
        print(estadisticas_df[['Player', 'Age']])
        
        # Cuenta con cuantos jugadores tienen mas de 30 años
        mayores_de_30 = estadisticas_df[estadisticas_df['Age'] > 30]
        cantidad_mayores_de_30 = len(mayores_de_30)
        print(f"\nCantidad de jugadores mayores de 30 años: {cantidad_mayores_de_30}")


navegador.quit() 




