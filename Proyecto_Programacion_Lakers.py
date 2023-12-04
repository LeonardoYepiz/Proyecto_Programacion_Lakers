#Proyecto Programacion 5to semestre
#Web Scraping del equipo Los Angeles Lakers temporada 2022-2023

from bs4 import BeautifulSoup
import requests

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

