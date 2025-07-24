from bs4 import BeautifulSoup
import requests
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# exploraremos el ranking global de artistas en kworb
url = 'https://kworb.net/itunes/'

# cabecera para simular que el acceso viene de un navegador
headers = {"User-Agent": "Mozilla/5.0 (Web Scraping Bot)"}

# request get para ver si es exitoso
respuesta = requests.get(url, headers=headers)

# analizamos el html
sopa = BeautifulSoup(respuesta.text,'html.parser')

# buscamos una tabla
tabla = sopa.find('table')

# los encabezados de una tabla en html están dentro de la etiqueta thead separador th
encabezados = [th.get_text(strip=True) for th in tabla.find('thead').find_all('th')]

datos = []

# en html las filas de una tabla están dentro de las etiquetas tr
# dentro del tbody de la tabla
filas = tabla.find("tbody").find_all('tr')

# ahora extraemos cada dato dentro de td
for fila in filas:
    celdas = []
    for celda in fila.find_all('td'):
        celdas.append(celda.text.strip().replace("\n", " "))
    datos.append(celdas)

df = pd.DataFrame(datos,columns=encabezados)

# crear una base de datros
conn = sqlite3.connect('global_top_artists.db')
cursor = conn.cursor()

# create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS global_top_artists (
    position INTEGER,
    growth TEXT,
    artist TEXT,
    points INTEGER,
    apple INTEGER,
    spotify INTEGER,
    itunes INTEGER,
    youtube INTEGER, 
    shazam INTEGER, 
    deezer INTEGER,
    top_country TEXT, 
    top_number INTEGER
)
''')

# insertar valores
df.to_sql('global_top_artists', conn, if_exists='replace', index=False)

# commit
conn.commit()

# cierra la conexion
conn.close()

print("Base de datos 'global_top_artists.db' creada y llenada exitosamente.")

# convertir columnas numericas a numericos
columnas = ['Pos','Points','Apple M','Spotify','iTunes','YouTube','Shazam','Deezer', '#']
for columna in columnas:
    df[columna] = df[columna].astype(str).astype(int)

# visualizacion 1
# Top 5 artistas por puntos
top_artistas = df.sort_values(by='Points', ascending=False).head(5)

# Plataformas en millones
plataformas = ['Apple M', 'Spotify', 'iTunes', 'YouTube', 'Shazam', 'Deezer']

# Gráfico apilado
top_artistas.set_index('Artist')[plataformas].plot(kind='bar', stacked=True, figsize=(10,6))

plt.title('Streams por plataforma (Top 5 artistas)')
plt.ylabel('Streams (millones)')
plt.xlabel('Artista')
plt.legend(title='Plataforma')
plt.tight_layout()
plt.show()

# visualizacion 2
# agrupar por pais y sumar reproducciones
heatmap_data = df.groupby('Top Country')[plataformas].sum()
heatmap_data['total_streams'] = heatmap_data.select_dtypes(include='number').sum(axis=1)

# obtenemos los 10 países para que el heatmap se visualice mejor
top_countries = heatmap_data.sort_values(by='total_streams', ascending = False).head(10)
top_countries_list = top_countries.loc[:,plataformas]

# reproducciones por país y plataforma
plt.figure(figsize=(12,8))
sns.heatmap(top_countries_list)
plt.title('Reproducciones por país y plataforma')
plt.xlabel('Plataforma')
plt.ylabel('País')
plt.show()

# total de streams
df['Total Streams'] = df[plataformas].sum(axis=1)

plt.figure(figsize=(10,6))
plt.scatter(df['Total Streams'],df['Pos'], alpha=0.6)

plt.title('Posición vs Total de Streams')
plt.xlabel('Posición en el ranking')
plt.ylabel('Total de streams (millones)')
plt.grid(True)
plt.tight_layout()
plt.show()


