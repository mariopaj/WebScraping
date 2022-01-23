# Importamos librerías necesarias para escrapear

from selenium import webdriver 

import time  

import requests as req

from bs4 import BeautifulSoup as bs

import pandas as pd

from webdriver_manager.chrome import ChromeDriverManager

PATH=ChromeDriverManager().install()

driver=webdriver.Chrome(PATH)

driver.get('https://tienda.mercadona.es/')

'''En esta parte sacamos todo el HTML de la página de Mercadona'''

# Aceptamos las cookies
driver.find_element_by_xpath('//*[@id="root"]/div[1]/div/div/button[2]').click()
time.sleep(2)

# Introducimos el código postal
driver.find_element_by_xpath('//*[@id="root"]/div[4]/div/div[2]/div/form/div/input').send_keys('28001')

# Continuamos
driver.find_element_by_xpath('//*[@id="root"]/div[4]/div/div[2]/div/form/button').click()
time.sleep(2)

# Vamos a categorías
driver.find_element_by_xpath('//*[@id="root"]/header/div[1]/nav/a[1]').click()
time.sleep(2)

## Aquí comienza el escrapeo
html = [] # Hay 26 categorías y 155 (len(html) = 155)

for i in range(2, 28):
    while 1:
        
        # Vamos sacando el html de cada página
        html.append(bs(driver.page_source, 'html.parser'))
        try:
            # Clicamos al botón de ver siguiente subcategoría
            driver.find_element_by_xpath('//*[@id="root"]/div[2]/div[2]/div[1]/div/div/button').click()
            time.sleep(2)
        except:
            break

    # Clicamos en la categoría siguiente
    try:
        driver.find_element_by_xpath('//*[@id="root"]/div[2]/div[1]/ul/li[{}]/div/button/span/label'.format(i)).click()
        time.sleep(2)
    except:
        break
        
driver.quit() # Apagamos el driver

'''En esta parte vamos sacando la información que nos interesa de cada producto (nombre, descripción, precio y URL de la imagen del producto)'''

# Sacamos el nombre de los productos de todas las subcategorías
nombres = []

for i in range(155):
    nombres.append(html[i].find_all(class_='subhead1-r product-cell__description-name'))

# Desglosamos la lista en una sola
nombres_list = []

for item in nombres:
    nombres_list += item
    
# Sacamos el texto de la lista
nombres = [nombre.text for nombre in nombres_list]

# Sacamos los precios de todas las subcategorías
precios = []

for i in range(155):
    precios.append(html[i].find_all(class_='product-price__unit-price subhead1-b'))

# Desglosamos la lista en una sola
precios_list = []

for item in precios:
    precios_list += item
    
# Sacamos el texto de la lista
precios = [precio.text for precio in precios_list]

# Sacamos la descripcion de todas las subcategorías
descripcion = []

# Sacamos la descripción de los productos por subcategorías
for i in range(155):
    descripcion.append(html[i].find_all('div', class_='product-format product-format__size--cell'))
    
# Desglosamos la lista en una sola
descripcion_list = []

for item in descripcion:
    descripcion_list += item
    
# Sacamos el texto de la lista
descripcion = [descripcion.text for descripcion in descripcion_list]

# Sacamos las URLs de las imágenes de todas las subcategorías
imagenes = []

# Sacamos la URL de los productos por subcategoría
for i in range(155):
    imagenes.append(html[i].find_all(class_='product-cell__image-wrapper'))

# Desglosamos la lista en una sola
imagenes_list = []

for item in imagenes:
    imagenes_list += item
    
# Sacamos la URl de la imagen de cada producto
imagenes = [imagen.find('img').attrs['src'] for imagen in imagenes_list]

# Creamos el DataFrame de los productos a través de un dicionario
productos = pd.DataFrame({'nombre': nombres,
           'descripcion': descripcion,
           'precio': precios,
           'imagen': imagenes})

'''Esta parte está dedicada a la limpieza y a la implementación de la variable subcategoría para ampliar informaión'''

# Convertimos los precios en float y los strings los pasamos a minúsculas
productos['precio'] = productos.precio.apply(lambda x: x.replace('€', '').strip())
productos['precio'] = productos.precio.apply(lambda x: float(x.replace(',', '.')))
productos['nombre'] = productos.nombre.apply(lambda x: x.lower())
productos['descripcion'] = productos.descripcion.apply(lambda x: x.lower())

# Sacamos las subcategorías
subcategorias = []

for i in range(155):
    subcategorias.append(html[i].find_all(class_='category-detail__title title1-b'))
    
# Desglosamos la lista en una sola
subcategorias_list = []

for item in subcategorias:
    subcategorias_list += item
    
# Sacamos los nombres de lsa subcategorias en minúscula
subcategorias = [subcategoria.text.lower() for subcategoria in subcategorias_list]

# Vemos el número de productos por subcategoría
numero_productos = []

for i in range(155):
    numero_productos.append(len(html[i].find_all(class_='product-cell')))

# Creamos una lista con todos los nombres de las subcategorías en función del número de productos
numbers = list(range(155))
subcategoria_columna = []

for i, j in enumerate(numbers):
    subcategoria_columna.append(numero_productos[i] * [subcategorias[j]])
    
# Desglosamos la lista en una sola
subcategorias_columna_list = []

for item in subcategoria_columna:
    subcategorias_columna_list += item

# Añadimos al DataFrame la columna subcategoría

productos['subcategoria'] = subcategorias_columna_list

# Exportamos a CSV y a XLSX
productos.to_csv(r'C:\Users\HP\Dropbox\Mi PC (DESKTOP-KE4BQ28)\Desktop\Proyecto página web comparador de precios\productos_mercadona.csv', index = False)
productos.to_excel(r'C:\Users\HP\Dropbox\Mi PC (DESKTOP-KE4BQ28)\Desktop\Proyecto página web comparador de precios\productos_mercadona.xlsx', index = False)