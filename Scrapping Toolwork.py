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

url = "https://www.b2b.kupfer.cl/productos-con-acuerdo/seguridad-industrial.html"
navegador.get(url)
data = []

time.sleep(3)

def scrap_kupfer():
    while True:

        elementos_listado = navegador.find_elements(By.CSS_SELECTOR, 'li.product-item')

        print(f"{len(elementos_listado)} items found")

        for elemento in elementos_listado:
            try:
                titulo_elemento = elemento.find_element(By.CSS_SELECTOR, 'a.product-item-link')
                try:
                    precio_elemento = elemento.find_element(By.CSS_SELECTOR, 'span.price')
                except NoSuchElementException:
                    precio_elemento = None

                imagen = elemento.find_element(By.TAG_NAME, 'img').get_attribute('src')

                data.append({
                    'Titulo': titulo_elemento.text,
                    'Precio': precio_elemento.text,
                    'Imagen': imagen,
                })
            except NoSuchElementException:
                pass

            print(f"Se han encontrado {titulo_elemento.text}")

        try:
            siguiente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.action.next')))
            navegador.execute_script("arguments[0].scrollIntoView(true);", siguiente)
            time.sleep(1)
            siguiente.click()
            time.sleep(3)
        except (NoSuchElementException, TimeoutException):
            print("No hay más páginas para mostrar")
            break

scrap_kupfer()

df = pd.DataFrame(data)
df.to_csv('scrapping.csv', index=False)

navegador.quit()
