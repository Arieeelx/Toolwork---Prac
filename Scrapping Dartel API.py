import requests
import pandas as pd
import time


def obtener_todas_las_categorias():
    """
    TODAS LAS CATEGORÍAS DISPONIBLES DESDE LA ÚLTIMA CARGA REALIZADA EN JSON
    """
    url_api = "https://www.dartel.cl/api/catalog_system/pub/category/tree/3"

    try:

        #SE REALIZA LA CONFIGURACION DE LA REQUEST PARA LA API
        response = requests.get(url_api, timeout=10)
        categorias = response.json()

        #SE CREA LA VARIABLE PARA EL DICCIONARIO DE LAS CATEGORIAS
        categorias_dict = {}

        for cat in categorias:
            nombre = cat.get('name', '').lower().replace(' ', '_').replace('/', '_')
            url = cat.get('url', '')

            if url:
                categorias_dict[nombre] = f"https://www.dartel.cl{url}"

            # SI TIENE CATEGORIAS...
            if 'children' in cat and cat['children']:
                for subcat in cat['children']:
                    subnombre = subcat.get('name', '').lower().replace(' ', '_').replace('/', '_')
                    suburl = subcat.get('url', '')
                    if suburl:
                        categorias_dict[f"{nombre}_{subnombre}"] = f"https://www.dartel.cl{suburl}"

        return categorias_dict

    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        return {}


def scrap_dartel_api(url, categoria_nombre):
    """
    Scrapea una categoría completa usando API de VTEX
    Incluye productos CON y SIN stock
    """
    categoria_path = url.replace("https://www.dartel.cl", "")
    api_url = f"https://www.dartel.cl/api/catalog_system/pub/products/search{categoria_path}"

    data = []
    pagina = 0
    max_paginas = 200 # <<<<<<<<Límite de seguridad>>>>>>>>
    intentos_vacios = 0

    print(f"[{categoria_nombre}] Consultando API...")

    while pagina < max_paginas:
        # VTEX PAG 50-50
        url_paginada = f"{api_url}?_from={pagina * 50}&_to={(pagina + 1) * 50 - 1}"

        try:
            response = requests.get(url_paginada, timeout=15)

            if response.status_code not in  [200, 206]:
                print(f"  ⚠️ Status code: {response.status_code} - Deteniendo categoría")
                break

            productos = response.json()

            if not productos or len(productos) == 0:
                intentos_vacios += 1
                print(f" Página {pagina + 1} vacía (Intento {intentos_vacios}/3")

                if intentos_vacios >= 3:
                    print(f" Fin de productos después de 3 intentos vacíos")
                    break

                pagina += 1
                continue

            intentos_vacios = 0

            for producto in productos:
                try:
                    # DATOS BASICOS
                    product_id = producto.get('productId', 'N/A')
                    titulo = producto.get('productName', 'N/A')
                    marca = producto.get('brand', 'N/A')
                    descripcion = producto.get('description', 'N/A')

                    # CONTENIDO ITEMS (variaciones del producto)
                    items = producto.get('items', [])

                    if items:
                        for item in items:
                            # SKU
                            sku = item.get('itemId', product_id)
                            nombre_item = item.get('name', titulo)

                            # VENDEDOR
                            sellers = item.get('sellers', [])

                            if sellers:
                                seller = sellers[0]
                                oferta = seller.get('commertialOffer', {})

                                # PRECIO Y STOCK
                                precio = oferta.get('Price', 0)
                                precio_lista = oferta.get('ListPrice', 0)
                                stock = oferta.get('AvailableQuantity', 0)

                                # IMAGEN
                                imagenes = item.get('images', [])
                                imagen = imagenes[0].get('imageUrl', 'N/A') if imagenes else 'N/A'

                                # EAN <<<<<<<CODIGO DE BARRAS>>>>>>>
                                ean = item.get('ean', 'N/A')

                                #COLUMNAS DEL CSV
                                data.append({
                                    'Categoria': categoria_nombre,
                                    'Marca': marca,
                                    'Nombre_Item': nombre_item,
                                    'Descripción': descripcion,
                                    'Product_ID': product_id,
                                    'SKU': sku,
                                    'Código Proovedor': ean,
                                    'Stock': stock,
                                    'Precio': f"${precio:,.0f}" if precio > 0 else 'Sin precio',
                                    'Precio_Lista': f"${precio_lista:,.0f}" if precio_lista > 0 else 'Sin precio',
                                    'Imagen': imagen,
                                    'URL': f"https://www.dartel.cl{producto.get('link', '')}",
                                })
                    else:
                        # PRODUCTO SIN ITEMS
                        data.append({
                            'Categoria': categoria_nombre,
                            'Marca': marca,
                            'Nombre_Item': titulo,
                            'Descripción': descripcion,
                            'Product_ID': product_id,
                            'SKU': 'N/A',
                            'Código Proovedor': 'NA',
                            'Stock': 'Sin stock',
                            'Precio': 'Sin precio',
                            'Precio_Lista': 'Sin precio',
                            'Imagen': 'N/A',
                            'URL': f"https://www.dartel.cl{producto.get('link', '')}",
                        })

                except Exception as e:
                    print(f"  ✗ Error procesando producto: {e}")
                    continue

            print(f"  Página {pagina + 1}: {len(productos)} productos | Acumulado: {len(data)}")
            pagina += 1
            time.sleep(0.5)  # STOP ENTRE REQUEST'S

        except Exception as e:
            print(f"  ✗ Error en request: {e}")
            break

    return data


# ========================================
# EJECUCIÓN PRINCIPAL
# ========================================

print("\n" + "=" * 70)
print("SCRAPING COMPLETO DE DARTEL VÍA API VTEX")
print("=" * 70 + "\n")

# CLASIFICACION DE CATEGORIAS AUTOMATICO:
print("Obteniendo lista de categorías...\n")
url_categorias = obtener_todas_las_categorias()

if not url_categorias:
    # EN CASO DE ERROR: LISTA MANUAL DE USO
    print("Usando lista manual de categorías\n")
    url_categorias = {
        'automatizacion_control': 'https://www.dartel.cl/automatizacion-y-control',
        'calidad_energia': 'https://www.dartel.cl/calidad-de-energia',
        'canalizaciones': 'https://www.dartel.cl/canalizaciones',
        'conductores': 'https://www.dartel.cl/conductores',
        'conectividad_redes': 'https://www.dartel.cl/conectividad-y-redes',
        'distribucion_electrica': 'https://www.dartel.cl/distribucion-electrica',
        'energias_renovables': 'https://www.dartel.cl/energias-renovables-y-electromovilidad',
        'ferreteria_electrica': 'https://www.dartel.cl/ferreteria-electrica',
        'iluminacion': 'https://www.dartel.cl/iluminacion',
        'instalaciones_residenciales': 'https://www.dartel.cl/instalaciones-residenciales',
        'instrumentos_medida': 'https://www.dartel.cl/instrumentos-de-medida',
        'materiales_apex': 'https://www.dartel.cl/materiales-a-prueba-de-explosion-apex',
        'media_tension': 'https://www.dartel.cl/media-tension',
        'motores_electricos': 'https://www.dartel.cl/motores-electricos',
        'otros': 'https://www.dartel.cl/otros',
        'respaldo_energetico': 'https://www.dartel.cl/respaldo-energetico',
        'sistema_conexion_tierra': 'https://www.dartel.cl/sistema-de-conexion-a-tierra'
    }

print(f"Total de categorías a scrapear: {len(url_categorias)}\n")

todos_los_datos = []

for i, (categoria, url) in enumerate(url_categorias.items(), 1):
    print(f"\n[{i}/{len(url_categorias)}] {categoria.upper()}")
    print(f"URL: {url}")

    datos_categoria = scrap_dartel_api(url, categoria)
    todos_los_datos.extend(datos_categoria)

    print(f"✓ {len(datos_categoria)} productos scrapeados de {categoria}")
    print("-" * 70)

# ARCHIVO CSV
df = pd.DataFrame(todos_los_datos)
df.to_csv('scrapping_Dartel.csv', index=False, encoding='utf-8-sig')

print("\n" + "=" * 70)
print(f"✓ SCRAPING COMPLETADO")
print(f"✓ Total productos: {len(todos_los_datos)}")
print(f"✓ Con stock: {len(df[df['Stock'] > 0])}")
print(f"✓ Sin stock: {len(df[df['Stock'] == 0])}")
print(f"✓ Archivo: scrapping_Dartel.csv")
print("=" * 70 + "\n")