#Proyecto Programacion 5to semestre
#Web Scraping del equipo Los Angeles Lakers temporada 2022-2023

from bs4 import BeautifulSoup
import requests
import pandas as pd

pagina=("https://www.basketball-reference.com/teams/LAL/2023.html")
resultado=requests.get(pagina)
contenido=resultado.text

soup=BeautifulSoup(contenido, "lxml")
#print(soup.prettify())
titulo=soup.find("h1").get_text(strip= "True", separator= " ")
print("El titulo de la pagina es el siguiente:", titulo)

informacion = soup.find("div", {"id": "info"}).get_text(strip=True, separator=" ")


informacion_por_renglones = informacion.split('\n')
print("La informacion de la pagina principal es la siguiente:")
for linea in informacion_por_renglones:
    print(linea)

jugadores_div=soup.find("div", {"id":"div_roster"})

if jugadores_div:
    tabla=jugadores_div.find("table", {"class":"sortable"})

    if tabla:
        datos_jugadores=[]

        filas=tabla.find_all("tr")

        for fila in filas[1:]:
            datos=fila.find_all(["th,"td])
            jugador=[dato.get_text(strip=True) for dato in datos]

        columnas=[header.get_text(strip=True) for header in filas [0].find_all("th")

        data_df=pd.DataFrame(datos_jugadores,columns=columnas)
        print("La informacion de los jugadores es la siguiente:", data_df)












