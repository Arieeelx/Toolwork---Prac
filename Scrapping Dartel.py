from logging import exception

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import time

url_categorias = {
    #'automatizacion_control': 'https://www.dartel.cl/automatizacion-y-control',
    #'calidad_energia': 'https://www.dartel.cl/calidad-de-energia',
    #'canalizaciones': 'https://www.dartel.cl/canalizaciones',
    #'conductores': 'https://www.dartel.cl/conductores',
    #'conectividad_redes': 'https://www.dartel.cl/conectividad-y-redes',
    #'distribucion_electrica': 'https://www.dartel.cl/distribucion-electrica',
    #'energias_renovables_electromovilidad': 'https://www.dartel.cl/energias-renovables-y-electromovilidad',
    #'ferreteria_electrica': 'https://www.dartel.cl/ferreteria-electrica',
    #'iluminacion': 'https://www.dartel.cl/iluminacion',
    #'instalaciones_residenciales': 'https://www.dartel.cl/instalaciones-residenciales',
    #'instrumentos_medida': 'https://www.dartel.cl/instrumentos-de-medida',
    #'materiales_prueba_explosion_apex': 'https://www.dartel.cl/materiales-a-prueba-de-explosion-apex',
    #'media_tension': 'https://www.dartel.cl/media-tension',
    'motores_electricos': 'https://www.dartel.cl/motores-electricos',
    #'otros': 'https://www.dartel.cl/otros',
    #'respaldo_energetico': 'https://www.dartel.cl/respaldo-energetico',
    'sistema_conexion_tierra': 'https://www.dartel.cl/sistema-de-conexion-a-tierra'
}

def scrap_dartel(url, categoria_nombre):
    navegador.get(url)
    time.sleep(3)

    productos_vistos = set()
    intentos_sin_cambio = 0

    # CERRAR POPUP DE OFERTA
    try:
        cerrar_popup = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[name()='use' and contains(@href, 'sti-close')]/ancestor::button")))
        cerrar_popup.click()
        print("POPUP CERRADO\n")
        time.sleep(1)
    except (NoSuchElementException, TimeoutException):
        print("No existe POPUP\n")
        pass

    data = []

    while True:
        time.sleep(2)

        navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        elementos_listado = navegador.find_elements(By.CSS_SELECTOR, 'section.vtex-product-summary-2-x-container')
        productos_antes = len(productos_vistos)

        print(f"[{categoria_nombre}] {len(elementos_listado)} Items vistos | {len(productos_vistos)} únicos scrapeados")

        for elemento in elementos_listado:
            try:

                try:
                    sku_elemento = elemento.find_element(By.CSS_SELECTOR, "span.vtex-product-identifier-0-x-product-identifier__value")
                    sku_text = sku_elemento.text
                except NoSuchElementException:
                    sku_text = None

                if sku_text and sku_text in productos_vistos:
                    continue

                if sku_text:
                    productos_vistos.add(sku_text)

                try:
                    marca_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.vtex-store-components-3-x-productBrandName')
                except NoSuchElementException:
                    marca_elemento = None

                try:
                    titulo_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.vtex-product-summary-2-x-productBrand')
                except NoSuchElementException:
                    titulo_elemento = None

                try:
                    stock_elemento = elemento.find_element(By.CSS_SELECTOR, "p.dartelcl-product-price-custom-0-x-nameFranquicia")
                except NoSuchElementException:
                    stock_elemento = None

                try:
                    partes = elemento.find_elements(By.CSS_SELECTOR, "span.dartelcl-product-price-custom-0-x-currencyInteger")

                    if len(partes) >= 2:
                        parte_entera = partes[0].text.replace(",", "").replace(".", "")
                        parte_decimal = partes[1].text.replace(",", "").replace(".", "")
                        precio_text = f"${parte_entera}.{parte_decimal}"

                    elif len(partes) == 1:
                        parte_entera = partes[0].text.replace(",", "").replace(".", "")
                        precio_text = f"${parte_entera}"

                    else:
                        precio_text = "Sin precio"

                except (NoSuchElementException, IndexError):
                    precio_text= "Sin precio"

                try:
                    imagen = elemento.find_element(By.TAG_NAME, "img").get_attribute('src')
                except NoSuchElementException:
                    imagen = None

                marca_text = marca_elemento.text if marca_elemento else 'NA'
                titulo_text = titulo_elemento.text if titulo_elemento else 'NA'
                stock_text = stock_elemento.text if stock_elemento else 'Sin información stock'

                data.append({
                    'marca': marca_text,
                    'titulo': titulo_text,
                    'sku': sku_text if sku_text else 'NA',
                    'stock': stock_text,
                    'precio': precio_text,
                    'imagen': imagen if imagen else 'NA',
                })

                print(f"Se han encontrado {titulo_elemento.text}, precio: {precio_text}, marca: {marca_text}")

            except Exception as e:
                print(f"x Error al scrapear producto: {e}")
                continue

        productos_despues = len(productos_vistos)

        if productos_despues == productos_antes:
            intentos_sin_cambio += 1
            print(f"No se encontraron productos nuevos (intento {intentos_sin_cambio}/3)")
        else:
            intentos_sin_cambio = 0

        if intentos_sin_cambio >= 3:
            print(f"{categoria_nombre} No hay más productos después de 3 intentos\n")
            break

        try:
            boton_cargar_mas = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"div.vtex-button__label.flex.items-center.justify-center.h-100.ph5")))

            navegador.execute_script("arguments[0].scrollIntoView(true);", boton_cargar_mas)
            time.sleep(1)
            boton_cargar_mas.click()
            print(f" -> Click en 'Cargar más'")
            time.sleep(3)

        except (NoSuchElementException, TimeoutException):
            print(f"[{categoria_nombre}] No hay más botón 'Cargar más'")
            break
    return data

navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

todos_los_datos = []

print(f"INICIANDO SCRAPING DE {len(url_categorias)} CATEGORÍAS")

for i, (categoria, url) in enumerate(url_categorias.items(), 1):
    print(f"Scrapeando categoría: {categoria.upper()}")
    print(f"URL: {url}")

    datos_categoria = scrap_dartel(url, categoria)
    todos_los_datos.extend(datos_categoria)

    print(f" {len(datos_categoria)} productos scrapeados de {categoria}")

df = pd.DataFrame(todos_los_datos)
df.to_csv('scrapping_Dartel.csv', index=False, encoding='utf-8-sig')

print(f"Total productos scrapeados: {len(todos_los_datos)}")

navegador.quit()
