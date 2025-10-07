from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
import time

navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

url = "https://www.b2b.kupfer.cl/productos-con-acuerdo/seguridad-industrial.html?p=1&product_list_limit=36"
navegador.get(url)
time.sleep(3)


def scrap_kupfer():
    data = []

    while True:

        elementos_listado = navegador.find_elements(By.CSS_SELECTOR, 'li.product-item')
        print(f"{len(elementos_listado)} Items encontrados listo para scrapping")

        for elemento in elementos_listado:
            try:
                titulo_elemento = elemento.find_element(By.CSS_SELECTOR, 'a.product-item-link')

                try:
                    sku_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.product-item-sku')
                except NoSuchElementException:
                    sku_elemento = None

                try:
                    precio_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.price')
                except NoSuchElementException:
                    precio_elemento = None

                try:
                    imagen = elemento.find_element(By.TAG_NAME, 'img').get_attribute('src')
                except NoSuchElementException:
                    imagen = None

                titulo_text = titulo_elemento.text if titulo_elemento else 'N/A'
                sku_text = sku_elemento.text if sku_elemento else 'N/A'
                precio_text = precio_elemento.text if precio_elemento else 'Sin precio'

                data.append({
                    'Titulo': titulo_text,
                    'Sku': sku_text,
                    'Precio': precio_text,
                    'Imagen': imagen if imagen else 'N/A',
                })
            except NoSuchElementException:
                continue

            print(f"Se han encontrado {titulo_elemento.text}")

        try:
            siguiente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.action.next')))
            navegador.execute_script("arguments[0].scrollIntoView(true);", siguiente)
            siguiente.click()
            time.sleep(1)
        except (NoSuchElementException, TimeoutException):
            print("No hay más páginas para mostrar")
            break

    return data

data = scrap_kupfer()

print(f"{len(data)} Items scrapeados")

df = pd.DataFrame(data)
df.to_csv('scrapping.csv', index=False, encoding='utf-8-sig')

navegador.quit()
