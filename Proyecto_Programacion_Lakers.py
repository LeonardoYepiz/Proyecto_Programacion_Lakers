from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import plotly.express as px
from dash import Dash, dcc, html, dash_table, callback, Input, Output

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

#Sacar informacion de jugadores
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

        # Agregar una columna para la nacionalidad si no existe
        columnas = [header.get_text(strip=True) for header in filas[0].find_all("th")]
        if 'birth_country' not in columnas:
            columnas.append('birth_country')

        data_jugadores = []
        for fila in filas[1:]:
            jugador = [dato.get_text(strip=True) for dato in fila.find_all(["th", "td"])]

            # Obtener información de nacionalidad si está disponible
            nacionalidad = fila.find("td", {"data-stat": "birth_country"})
            if nacionalidad:
                jugador.append(nacionalidad.get_text(strip=True))
            else:
                jugador.append('N/A')

            data_jugadores.append(jugador)

        # Crear el DataFrame con la información de los jugadores 
        data_jugadores_df = pd.DataFrame(data_jugadores, columns=columnas)

        # Mostrar información de todos los jugadores 
        print("Información de todos los jugadores:")
        print(data_jugadores_df.drop(columns=['birth_country']))

        # DataFrame con solo el nombre y la nacionalidad
        jugadores_nacionalidad_df = data_jugadores_df[['Player', 'birth_country']]
        print("\nNombre de los jugadores y su nacionalidad:")
        print(jugadores_nacionalidad_df)

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

# dashboard asistentes:
data_asistentes = pd.read_csv("C:/Users/Rebeca R/Downloads/asistentes.csv")

def dashboard():
    body = html.Div([
        html.H2("Datos de Asistentes"),
        html.P("Objetivo del DashBoard: Mostrar los datos de los asistentes."),
        html.Hr(),
        dcc.Dropdown(
            id="ddAsistentes",
            options=[
                {"label": asistente, "value": asistente} for asistente in data_asistentes["Nombre"]
            ],
            multi=True,
            value=[data_asistentes["Nombre"].iloc[0]],
            style={'width': '50%'}
        ),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in data_asistentes.columns],
            data=data_asistentes.to_dict("records"),
            page_size=10
        ),
        dcc.Graph(id="figAsistentes")
    ])
    return body

@callback(
    Output("figAsistentes", "figure"),
    Input("ddAsistentes", "value")
)
def update_grafica(selected_asistentes):
    filtered_data = data_asistentes[data_asistentes["Nombre"].isin(selected_asistentes)]
    fig = px.line(filtered_data, x="Nombre", y="Cargo", title="Cargos de Asistentes")
    return fig

if __name__== "__main__":
    print("Ejecutando la aplicación Dash.")
    app = Dash(__name__)
    app.layout = dashboard()
    app.run_server(debug=True, host='127.0.0.1', port=8050)



