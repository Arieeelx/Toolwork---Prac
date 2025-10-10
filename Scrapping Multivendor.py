from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

# ========================================
# LOGIN PARA VER PRECIOS
# ========================================

print("🔐 Iniciando sesión en Multivendor!...")

navegador.get("https://tienda.multivendor.cl/ingresar")

try:
    # REEMPLAZA CON TUS CREDENCIALES
    email_input = wait.until(EC.element_to_be_clickable((By.NAME, "code")))  # Ajustar selector
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))  # Ajustar selector

    email_input.send_keys("SSSSS")
    password_input.send_keys("SSSSSS")

    # Click en botón login (ajustar selector)
    login_button = navegador.find_element(By.CSS_SELECTOR, "form button")
    login_button.click()

    print("✓ Credenciales ingresadas")
    time.sleep(1)  # Esperar que cargue después del login

    # Verificar si el login fue exitoso
    if "login" not in navegador.current_url.lower():
        print("✅ Login exitoso")
    else:
        print("❌ Login falló - Verificar credenciales o selectores")
        navegador.quit()
        exit()

except Exception as e:
    print(f"✗ Error en login: {e}\n")
    navegador.quit()
    exit()

time.sleep(2)

categoria = "https://tienda.multivendor.cl/c/herramientas-wokin-q3x4kjykgw"

print(f"Navegando a categoría: {categoria}")

navegador.get(categoria)
time.sleep(3)
tamano_anterior = navegador.execute_script("return document.body.scrollHeight")
pagina = 0

while True:
    navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        WebDriverWait(navegador, 10).until(lambda driver: driver.execute_script("return document.body.scrollHeight")> tamano_anterior)

        nuevo_tamano = navegador.execute_script("return document.body.scrollHeight")
        tamano_anterior = nuevo_tamano
        pagina = pagina + 1

        print(f"Scroll realizado, procediendo a cargar más contenido, scroll n°: {pagina}")

    except TimeoutException:
        print("✅ Scroll completado. Preparando SCRAP")
        break

def scrap_multivendor():

    data = []

    while True:

        elementos_listado = navegador.find_elements(By.CSS_SELECTOR, "div.sc-f671739f-0.djafFO")

        print(f"Productos: {len(elementos_listado)}")

        for elemento in elementos_listado:
            try:

                try:
                    titulo_elemento = elemento.find_element(By.CSS_SELECTOR, "a.sc-9ce670d8-0.sc-f671739f-3.gxqsIY.dYFEAL")
                except NoSuchElementException:
                    titulo_elemento = None

                try:
                    etiquetas_p_m = elemento.find_elements(By.CSS_SELECTOR, "p.truncate.text-tertiary")

                    if len(etiquetas_p_m) >= 2:
                        marca_elemento = etiquetas_p_m[0]
                        sku_elemento = etiquetas_p_m[1]
                    else:
                        marca_elemento = "NA"
                        sku_elemento = "NA"
                except NoSuchElementException:
                    sku_elemento = None
                    marca_elemento = None

                try:
                    precio_actual_elemento = elemento.find_element(By.CSS_SELECTOR, "span.sc-71dd7361-0.cgqXbq")
                    precio_antiguo_elemento = elemento.find_element(By.CSS_SELECTOR, "span.sc-71dd7361-0.eTcqKD")
                except NoSuchElementException:
                    precio_actual_elemento = None
                    precio_antiguo_elemento = None

                try:
                    stock_elemento = elemento.find_element(By.CSS_SELECTOR, "p.text-green-600")
                except NoSuchElementException:
                    stock_elemento = None


                titulo_text = titulo_elemento.text if titulo_elemento else "NA"
                sku_text = sku_elemento.text if sku_elemento else "NA"
                stock_text = stock_elemento.text if stock_elemento else "NA"
                precio_actual_text = precio_actual_elemento.text if precio_actual_elemento else "NA"
                precio_antiguo_text = precio_antiguo_elemento.text if precio_antiguo_elemento else "NA"
                marca_text = marca_elemento.text if marca_elemento else "NA"

                data.append({
                    "Titulo": titulo_text,
                    "Sku": sku_text,
                    "Stock": stock_text,
                    "Precio antiguo": precio_antiguo_text,
                    "Precio actual": precio_actual_text,
                    "Marca": marca_text,
                })

                print(f"->{titulo_text}")

            except Exception as e:
                print(f"Ocurrrio un error: {e}")

        return data

data = scrap_multivendor()

df = pd.DataFrame(data)
df.to_csv("scrapping_Multivendor.csv", index=False, encoding='utf-8')

navegador.quit()









