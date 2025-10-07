from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
import time

#CONTENIDO DE LOS URL'S DE CATEGORÍAS CON CANTIDAD MÁX DE 36 POR PÁGINA
url_categorias = {
    #'seguridad_industrial': 'https://www.b2b.kupfer.cl/productos-con-acuerdo/seguridad-industrial.html?product_list_limit=36',
    #'aceros_estructurales': 'https://www.b2b.kupfer.cl/aceros-estructurales.html?product_list_limit=36',
    #'aceros_inoxidables_aluminio': 'https://www.b2b.kupfer.cl/aceros-inoxidables-y-aluminio.html?product_list_limit=36',
    #'barras_acero': 'https://www.b2b.kupfer.cl/barras-de-acero.html?product_list_limit=36',
    #'canerias': 'https://www.b2b.kupfer.cl/ca-erias.html?product_list_limit=36',
    #'soldadura_corte': 'https://www.b2b.kupfer.cl/soldadura-y-corte.html?product_list_limit=36',
    #'equipos_herramientas_maquinas_industriales': 'https://www.b2b.kupfer.cl/equipos-herramientas-y-maquinarias-industriales.html?product_list_limit=36',
    #'mantencion_industrial': 'https://www.b2b.kupfer.cl/mantencion-industrial.html?product_list_limit=36',
    #'izaje_traccion': 'https://www.b2b.kupfer.cl/izaje-y-traccion.html?product_list_limit=36',
    #'pesca_cultivo': 'https://www.b2b.kupfer.cl/pesca-y-cultivo.html?product_list_limit=36',
    #'amarre': 'https://www.b2b.kupfer.cl/amarre.html?product_list_limit=36',
    #'potencia_oleohidraulica': 'https://www.b2b.kupfer.cl/potencia-oleohidraulica.html?product_list_limit=36',
    #'filtracion': 'https://www.b2b.kupfer.cl/filtracion.html?product_list_limit=36',
    #'mangueras_conexiones': 'https://www.b2b.kupfer.cl/mangueras-y-conexiones.html?product_list_limit=36#',
    'manejo_fluido': 'https://www.b2b.kupfer.cl/productos-con-acuerdo/manejo-de-fluido.html?product_list_limit=36',
    'equipos_energia': 'https://www.b2b.kupfer.cl/catalog/category/view/s/equipos-de-energia/id/1602/'
}

#FUNCIÓN PRINCIPAL QUE REALIZA SCRAPPING PARA KUPFER
def scrap_kupfer(url, categoria_nombre):
    navegador.get(url)


    data = []

    while True:


        elementos_listado = navegador.find_elements(By.CSS_SELECTOR, 'li.product-item')
        print(f"[{categoria_nombre}] {len(elementos_listado)} Items encontrados")

        #CONTENIDO PARA REALIZAR EL SCRAPPING DE CADA ELEMENTO
        for elemento in elementos_listado:
            try:
                titulo_elemento = elemento.find_element(By.CSS_SELECTOR, 'a.product-item-link')

                try:
                    sku_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.product-item-sku')
                except NoSuchElementException:
                    sku_elemento = None

                try:
                    precio_oferta_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.special-price span.price')
                except NoSuchElementException:
                    precio_oferta_elemento = None

                try:
                    precio_normal_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.price')
                except NoSuchElementException:
                    precio_normal_elemento = None

                try:
                    imagen = elemento.find_element(By.TAG_NAME, 'img').get_attribute('src')
                except NoSuchElementException:
                    imagen = None

                #SE GUARDAN EN VARIABLES
                titulo_text = titulo_elemento.text if titulo_elemento else 'N/A'
                sku_text = sku_elemento.text if sku_elemento else 'N/A'
                precio_oferta_text = precio_oferta_elemento.text if precio_oferta_elemento else 'No existe oferta'
                precio_normal_text = precio_normal_elemento.text if precio_normal_elemento else 'Sin precio'

                #SE AGREGA AL DATA LOS RESULTADOS
                data.append({
                    'Categoría': categoria_nombre,
                    'Titulo': titulo_text,
                    'Sku': sku_text,
                    'Precio oferta': precio_oferta_text,
                    'Precio normal': precio_normal_text,
                    'Imagen': imagen if imagen else 'N/A',
                })
                #AVISO DE QUE ARCHIVO SE VA AGREGANDO Y SUS PRECIOS RESPECTIVOS
                print(f"Se han encontrado {titulo_elemento.text}, precio oferta: {precio_oferta_text}, precio normal: {precio_normal_text}")

            except NoSuchElementException as e:
                print(f"x Error: {e}")
                continue

        #SENTENCIA PARA SCROLL DE PÁGINAS EN KUPFER
        try:
            siguiente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.action.next')))
            navegador.execute_script("arguments[0].scrollIntoView(true);", siguiente)
            siguiente.click()
            time.sleep(1)
        except (NoSuchElementException, TimeoutException):
            print(f"{categoria_nombre} <-- No hay más páginas para mostrar")
            break
    #IMPRIME EL VALOR A DATA
    return data

navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

todos_los_datos = []

print(f"INICIANDO SCRAPING DE {len(url_categorias)} CATEGORÍAS")

#BUCLE PARA COMPLETAR SCRAPPING EN LOS URL'S DE CATEGORÍAS
for i, (categoria, url) in enumerate(url_categorias.items(), 1):
    print(f"Scrapeando categoría: {categoria.upper()}")
    print(f"URL: {url}")

    datos_categoria = scrap_kupfer(url, categoria)
    todos_los_datos.extend(datos_categoria)

    print(f" {len(datos_categoria)} productos scrapeados de {categoria}")

df = pd.DataFrame(todos_los_datos)
df.to_csv('scrapping.csv', index=False, encoding='utf-8-sig')

print(f"Total: {len(todos_los_datos)} productos scrapeados")

navegador.quit()
