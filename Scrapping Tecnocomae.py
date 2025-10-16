from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# VARIABLES BÁSICAS GLOBAL
base_url = "https://www.tecnocomae.cl/search?q=bahco&page="
todos_productos = []


def extraer_producto(url_producto):
    #EXTRAE LA INFORMACION DEL PRODUCTO
    try:
        if not url_producto.startswith('http'):
            url_producto = f"https://www.tecnocomae.cl{url_producto}"

        print(f"   → Extrayendo: {url_producto}")


        response_producto = requests.get(url_producto)
        soup_producto = BeautifulSoup(response_producto.content, 'html.parser')

        stock = soup_producto.find('span', class_='product-form-stock')
        nombre = soup_producto.find('h1', class_='product-name')
        precio_compra = soup_producto.find('span', class_='product-form-price')
        precio_antiguo = soup_producto.find('span', class_='product-form-discount')
        marca = soup_producto.find('span', class_='product-form-brand')
        sku = soup_producto.find('span', class_='sku_elem')

        div_descrip = soup_producto.find('div', class_='col-12 description')
        if div_descrip:
            texto = div_descrip.text.strip()
        else:
            texto = 'NA'

        # Imagen
        div_sin_imagen = soup_producto.find('div', class_='product-page-no-image')

        if div_sin_imagen:
            imagen_url = 'Sin imagen'
        else:
            div_imagen = soup_producto.find('div', class_='main-product-image')

            if div_imagen:
                img = div_imagen.find('img')
                imagen_url = img.get('src')

                if imagen_url and not imagen_url.startswith('http'):
                    imagen_url = f"https://www.tecnocomae.cl{imagen_url}"
            else:
                imagen_url = 'NA'

        info_producto = {
            'Sku': sku.text.strip() if sku else 'NA',
            'Nombre': nombre.text.strip() if nombre else 'NA',
            'Descripción': texto,
            'Marca': marca.text.strip() if marca else 'NA',
            'Precio_compra': precio_compra.text.replace(' CLP', '').strip() if precio_compra else 'NA',
            'Precio_antiguo': precio_antiguo.text.strip() if precio_antiguo else 'NA',
            'Stock': stock.text.strip() if stock else 'NA',
            'Imagen': imagen_url,
        }

        print(f"      ✓ {info_producto['Nombre']}")
        return info_producto

    except Exception as e:
        print(f"      ❌ Error: {e}")
        return None


# Probar con 1 página primero
for pagina in range(1, 40):
    print(f"\n📄 Procesando página {pagina}")

    url = f"{base_url}{pagina}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    productos_pagina = soup.find_all('h3', class_='prod-title')

    print(f"   Encontrados {len(productos_pagina)} productos en esta página")

    # Recolectar URLs
    urls_productos = []
    for producto in productos_pagina:
        enlace = producto.find('a')
        if enlace:
            url_producto = enlace.get('href')
            urls_productos.append(url_producto)

    # Procesar X productos en paralelo
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(extraer_producto, url) for url in urls_productos]

        for future in as_completed(futures):
            resultado = future.result()
            if resultado:
                todos_productos.append(resultado)

    time.sleep(2)

df = pd.DataFrame(todos_productos)
df.to_csv("Scrapping_csv/productos_bahco.csv", index=False, encoding='utf-8')

print("📁 Datos guardados en 'productos_bahco.csv'")

print(f"\n✅ Total productos extraídos: {len(todos_productos)}")
print(todos_productos)