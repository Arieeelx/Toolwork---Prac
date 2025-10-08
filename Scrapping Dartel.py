from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import pandas as pd
import time

from script import boton_cargar_mas

'''url_categorias = {
    'automatizacion_control': 'https://www.dartel.cl/automatizacion-y-control'
    ''
    ''
    ''
    ''
    ''
    ''
    ''
    ''
    ''
}
   '''

navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

url = "https://www.dartel.cl/sistema-de-conexion-a-tierra"
navegador.get(url)

try:
    cerrar_popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[name()='use' and contains(@href, 'sti-close')]/ancestor::button")))
    cerrar_popup.click()
    print("POPUP CERRADO")
    time.sleep(1)
except (NoSuchElementException, TimeoutException):
    print("No se pudo cerrar el popup")
    pass

data = []
productos_vistos = set()
ultimo_conteo = 0

while True:

    elementos_listado = navegador.find_elements(By.CSS_SELECTOR, 'section.vtex-product-summary-2-x-container')
    print(f"Productos vistos: {len(elementos_listado)} items")

    for i, elemento in enumerate(elementos_listado, 1):

        try:

            try:
                sku_elemento = elemento.find_element(By.CSS_SELECTOR, "span.vtex-product-identifier-0-x-product-identifier__value")
                sku_text = sku_elemento.text
            except NoSuchElementException:
                sku_elemento = None

            if sku_text in productos_vistos:
                continue
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
                'sku': sku_text,
                'stock': stock_text,
                'precio': precio_text,
                'imagen': imagen,
            })

            print(f"Se han encontrado {titulo_elemento.text}, precio: {precio_text}, marca: {marca_text}")

        except StaleElementReferenceException:
            print(f"Elemento {i} ya no es válido, se salta")
            continue
        except Exception as e:
            print(f"x Error en producto {i}: {e}")
            continue
    if len(productos_vistos) == ultimo_conteo:
        try:
            boton_cargar_mas = navegador.find_element(By.CSS_SELECTOR, "div.vtex-button__label.flex.items-center.justify-center.h-100.ph5")
            if boton_cargar_mas.is_displayed() and boton_cargar_mas.is_enabled():
                boton_cargar_mas.click()
                print("Cargar más")
                continue
        except NoSuchElementException:
            break
    else:
        ultimo_conteo = len(productos_vistos)
        navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

print(f"Total productos scrapeados: {len(data)}")
df = pd.DataFrame(data)
df.to_csv('scrapping_Dartel.csv', index=False, encoding='utf-8-sig')

navegador.quit()
