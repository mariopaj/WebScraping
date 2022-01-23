# Importamos librerías necesarias para escrapear
import requests as req

from bs4 import BeautifulSoup as bs

import pandas as pd

# Importamos el excel creado de categorías y subcategorías
df_dia = pd.read_excel(r'C:\Users\mario\OneDrive\Escritorio\Proyecto Página Web\Escrapeo-DIA\DIA_cat.xlsx')

# Eliminamos las filas que no nos sirven
df_dia = df_dia.drop(df_dia.index[[0, 1]])

# Reseteamos el indice
df_dia.reset_index(inplace=True, drop=True)

# Renombramos columnas
df_dia.columns = ['cat', 'scat', 'npg']

''' Esta parte está dedicada a la creación de las URLs 
para hacer el request de ellas y extraer el HTML'''

url_cat = ['https://www.dia.es/compra-online/{}/'.format(cat) for cat in df_dia.cat.tolist()]

url_scat = []
for i, scat in enumerate(df_dia.scat.tolist()):
    url_scat.append(url_cat[i] + '{}/cf'.format(scat))

# Filtramos el DataFrame con las subcategorias que tienen más de una página
df_dia_filt = df_dia[df_dia.npg > 1]

index = df_dia_filt.index.to_list()

# Cogemos las URLs de las subcategorias que tienen más de una página
url_scat_filt = [url_scat[i] for i in index]

# Sacamos una lista del numero de páginas de cada subcategoría
npg = df_dia_filt.npg.tolist()

# Sacamos las URLs de las subcategorias que tienen varias páginas
new_url = []

for url, n in zip(url_scat_filt, npg):
    for i in range(1, n):
        new_url.append(url + '/cf?page={}&disp='.format(i))

# Unimos en una única lista todas las URLs
urls = url_scat + new_url

''' Esta parte la vamos a dedicar a extraer todo el HTML de las páginas 
y por consiguiente los datos necesarios'''

html = []

for url in urls:
    html.append(req.get(url).text)

soup = [bs(html[i], 'html.parser') for i in range(len(html))]

# Sacamos las celdas de los productos
products_grid_list = []

for i in range(len(soup)):
    products_grid_list.append(soup[i].find_all(class_ = 'product-list__item'))
    
# Desglosamos las listas
products_grid = []

for item in products_grid_list:
    products_grid += item

# Sacamos los links de las imágenes de los productos
product_img = []
for i in range(len(products_grid)):
    try:
        product_img.append(products_grid[i].find(class_ = 'crispImage').attrs['src'])
    except:
        product_img.append('') # En el caso de que el producto no tnga imagen introducimos en la lista ''

# Sacamos los nombres de los productos
product_name = []
for i in range(len(products_grid)):
    try:
        product_name.append(products_grid[i].find(class_ = 'details').text.strip().lower())
    except:
        product_name.append('')

# Sacamos los precios de los productos
product_price = []
for i in range(len(products_grid)):
    try:
        product_price.append(products_grid[i].find(class_ = 'price').text.strip())
    except:
        product_price.append('')

# Limpiamos los precios
product_price = [product_price[i][:4] for i in range(len(product_price))]
product_price = [float(product_price[i].replace(',', '.')) for i in range(len(product_price))]

# Vemos el número de productos que hay en cada página
n_products = []
for i in range(len(soup)):
    n_products.append(len(soup[i].find_all(class_ = 'product-list__item')))

# Sacamos la lista completa de los nombres de las subcategorías
scat_list = []

for scat, n in zip(products_scat, n_products):
    scat_list.append([scat]*n)

# Desglosamos las listas
scat_names = []

for item in scat_list:
    scat_names += item

# Vemos si el tamaño de todas las listas coincide
print(len(product_name), len(product_price), len(product_img), len(scat_names)) # Coinciden

# Cremos el DataFrame de los productos
df_dia_products = pd.DataFrame({'product' : product_name,
                                'price' : product_price,
                                'scat' : scat_names,
                                'img' : product_img})

# Exportamos el DataFrame a excel
df_dia_products.to_excel(r'C:\Users\mario\OneDrive\Escritorio\Proyecto Página Web\Escrapeo-DIA\productos_dia.xlsx', index = False)

