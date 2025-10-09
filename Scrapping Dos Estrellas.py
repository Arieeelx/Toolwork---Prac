from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

# ========================================
# PASO 1: HACER LOGIN
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

    email_input.send_keys("xxxxxxxx")
    password_input.send_keys("xxxxxx")

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

# ========================================
# PASO 2: EMPEZAMOS CON SCRAPPING
# ========================================

data = []

categoria = "https://dosestrellas.cl/lineas/5/agricultura-jardin"

print(f"Navegando a categoría: {categoria}")

navegador.get(categoria)
time.sleep(1)

navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)

while True:

    elementos_listado = navegador.find_elements(By.CSS_SELECTOR, "div.bodyProduct")
    print(f"{len(elementos_listado)} Items encontrados")

    for elemento in elementos_listado:
        try:
            try:
                titulo_elemento = elemento.find_element(By.CSS_SELECTOR, "a.name")
            except NoSuchElementException:
                titulo_texto = None

            try:
                sku_elemento = elemento.find_element(By.CSS_SELECTOR, "a.sku")
            except NoSuchElementException:
                sku_elemento = None


            titulo_text = titulo_elemento.text if titulo_elemento else "NA"
            sku_text = sku_elemento.text if sku_elemento else "NA"

            data.append({
                "titulo": titulo_text,
                "Sku": sku_text,
            })

            print(f"->{titulo_text}")

        except NoSuchElementException as e:
            print(f"x Error: {e}")
            continue

    break

df = pd.DataFrame(data)
df.to_csv("scrapping_DosEstrellas.csv")

navegador.quit()