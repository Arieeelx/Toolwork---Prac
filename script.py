import requests

# Tus dos URLs placeholder
urls_placeholder = [
    "https://www.b2b.kupfer.cl/media/catalog/product/P/R/PR5001BI30874_98118_ESPIGA_HEMBRA_BSP_RECTA_R1_R2_10_10_IMD.png?optimize=medium&bg-color=255,255,255&fit=bounds&height=300&width=240&canvas=240:300&format=jpeg",
    "https://www.b2b.kupfer.cl/media/catalog/product/P/R/PR22683BI30874_159617_Adaptador_Emsesa_MP_MP_8_8_IMD.png?optimize=medium&bg-color=255,255,255&fit=bounds&height=300&width=240&canvas=240:300&format=jpeg",
]

print("Verificando tamaño de imágenes placeholder:\n")

for i, url in enumerate(urls_placeholder, 1):
    try:
        response = requests.head(url, timeout=5)
        tamano = int(response.headers.get('Content-Length', 0))
        print(f"Placeholder {i}: {tamano:,} bytes ({tamano/1024:.2f} KB)")
    except Exception as e:
        print(f"Error: {e}")