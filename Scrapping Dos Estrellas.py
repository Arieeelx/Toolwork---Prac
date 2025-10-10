from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

# ========================================
# LOGIN PARA VER PRECIOS
# ========================================

print("🔐 Iniciando sesión en Dos Estrellas...")

navegador.get("https://dosestrellas.cl/home")  # Ajusta la URL de login

click_iniciar = navegador.find_element(By.CSS_SELECTOR, "div.icon-user")
click_iniciar.click()
time.sleep(2)

try:
    # REEMPLAZA CON TUS CREDENCIALES
    email_input = wait.until(EC.element_to_be_clickable((By.NAME, "email")))  # Ajustar selector
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))  # Ajustar selector

    email_input.send_keys("sssssss")
    password_input.send_keys("sssssssssss")

    # Click en botón login (ajustar selector)
    login_button = navegador.find_element(By.CSS_SELECTOR, "a.btn-login")
    login_button.click()

    print("✓ Credenciales ingresadas")
    time.sleep(1)  # Esperar que cargue después del login

    # Verificar si el login fue exitoso
    if "login" not in navegador.current_url.lower():
        print("Login exitoso")
    else:
        print("Login falló - Verificar credenciales o selectores")
        navegador.quit()
        exit()

except Exception as e:
    print(f"✗ Error en login: {e}\n")
    navegador.quit()
    exit()

# VARIABLES

categoria = "https://dosestrellas.cl/lineas/5/agricultura-jardin"

print(f"Navegando a categoría: {categoria}")

navegador.get(categoria)
time.sleep(1)

navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)
data = []

# ========================================
# FUNCION SCRAPPING
# ========================================

def scrap_dos_estrellas():

    while True:

        elementos_listado = navegador.find_elements(By.CSS_SELECTOR, "div.item")
        print(f"{len(elementos_listado)} Items encontrados")

        for elemento in elementos_listado:

            try:
                try:
                    stock_elemento = elemento.find_element(By.CSS_SELECTOR, "div.RangoStock")
                except NoSuchElementException:
                    stock_elemento = None

                try:
                    marca_elemento = elemento.find_element(By.CSS_SELECTOR, "a.marca")
                except NoSuchElementException:
                    marca_elemento = None

                try:
                    titulo_elemento = elemento.find_element(By.CSS_SELECTOR, "a.name")
                except NoSuchElementException:
                    titulo_elemento = None

                try:
                    sku_elemento = elemento.find_element(By.CSS_SELECTOR, "a.sku")
                except NoSuchElementException:
                    sku_elemento = None

                try:
                    precio_base_elemento = elemento.find_element(By.CSS_SELECTOR, "div.base")
                    precio_actual_elemento = elemento.find_element(By.CSS_SELECTOR, "span.precioFinal")
                except NoSuchElementException:
                    precio_base_elemento = None
                    precio_actual_elemento = None

                titulo_text = titulo_elemento.text if titulo_elemento else "NA"
                sku_text = sku_elemento.text if sku_elemento else "NA"
                precio_actual_text = precio_actual_elemento.text if precio_actual_elemento else "NA"
                precio_base_text = precio_base_elemento.text if precio_base_elemento else "NA"
                stock_text = stock_elemento.text if stock_elemento else 0
                marca_text = marca_elemento.text if marca_elemento else "NA"

                data.append({
                    "Marca": marca_text,
                    "Titulo": titulo_text,
                    "Sku": sku_text,
                    "Precio base": precio_base_text,
                    "Precio actual": precio_actual_text,
                    "Stock": stock_text
                })

                print(f"->Marca: {marca_text} || {titulo_text} || {precio_base_text} || Precio actual: {precio_actual_text} || Stock: {stock_text}")

            except NoSuchElementException as e:
                print(f"x Error: {e}")
                continue
        try:
            siguiente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.paginate.next')))
            navegador.execute_script("arguments[0].scrollIntoView(true);", siguiente)
            siguiente.click()
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            print(f"<-- No hay más páginas para mostrar")
            break

    return data

scrap_dos_estrellas()

df = pd.DataFrame(data)
df.to_csv("scrapping_DosEstrellas.csv", index=False, encoding='utf-8')

navegador.quit()