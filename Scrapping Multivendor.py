from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


navegador = webdriver.Chrome()
navegador.maximize_window()
wait = WebDriverWait(navegador, 10)

# ========================================
# LOGIN PARA VER PRECIOS
# ========================================

print("🔐 Iniciando sesión en Dos Estrellas...")

navegador.get("https://tienda.multivendor.cl/ingresar")  # Ajusta la URL de login

try:
    # REEMPLAZA CON TUS CREDENCIALES
    email_input = wait.until(EC.element_to_be_clickable((By.NAME, "code")))  # Ajustar selector
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))  # Ajustar selector

    email_input.send_keys("sssss")
    password_input.send_keys("sssss")

    # Click en botón login (ajustar selector)
    login_button = navegador.find_element(By.CSS_SELECTOR, "form button")
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


categoria = "https://tienda.multivendor.cl/c/herramientas-wokin-q3x4kjykgw"

print(f"Navegando a categoría: {categoria}")

navegador.get(categoria)
time.sleep(5)

navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)