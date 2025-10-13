import requests
import pandas as pd
import time

def obtener_todas_las_categorias():
    """
    TODAS LAS CATEGORÍAS DISPONIBLES DESDE LA ÚLTIMA CARGA REALIZADA EN JSON
    """
    url_api = "https://www.ferreteriamarsella.cl/api/catalog_system/pub/category/tree/3"

    try:
        # SE REALIZA LA CONFIGURACION DE LA REQUEST PARA LA API
        response = requests.get(url_api, timeout=10)
        categorias = response.json()

        # SE CREA LA VARIABLE PARA EL DICCIONARIO DE LAS CATEGORIAS
        categorias_dict = {}

        for cat in categorias:
            nombre = cat.get('name', '').lower().replace(" ", "_").replace("/", "_")
            url = cat.get('url', '')

            if url:
                categorias_dict[nombre] = f"https://www.ferreteriamarsella.cl{url}"

            # SI TIENE CATEGORIAS...
            if 'children' in cat and cat['children']:
                for subcat in cat['children']:
                    subnombre = subcat.get('name', '').lower().replace(" ", "_").replace("/", "_")
                    suburl = subcat.get('url', '')
                    if suburl:
                        categorias_dict[f"{nombre}_{subnombre}"] = f"https://www.ferreteriamarsella.cl{suburl}"

        return categorias_dict

    except Exception as e:
        print(f"Error obteniendo categorias: {e}")
        return {}

def scrap_marsella_api(url, categoria_nombre):

    """
    Scrapea una categoría completa usando API de VTEX
    Incluye productos CON y SIN stock
    """


    categoria_path = url.replace("https://www.ferreteriamarsella.cl", "")
    api_url = f"https://www.ferreteriamarsella.cl/api/catalog_system/pub/products/search{categoria_path}"

    data = []
    skus_vistos_en_categoria = set()
    pagina = 0
    max_paginas = 200 # <<<<<<<<Límite de seguridad>>>>>>>>
    intentos_vacios = 0

    print(f"[{categoria_nombre}] Consultando API...")

    while pagina < max_paginas:

        url_paginada = f"{api_url}?_from={pagina * 50 }&_to={(pagina + 1) * 50 - 1}"

        try:
            response = requests.get(url_paginada, timeout=10)

            if response.status_code not in [200, 206]:
                print(f" ⚠️ Status code: {response.status_code} - Deteniendo categoría")
                break

            productos = response.json()

            if not productos or len(productos) == 0:
                intentos_vacios += 1
                print(f" Página {pagina + 1} vacía (Intento {intentos_vacios}/3)")

                if intentos_vacios >= 3:
                    print(f" Fin de productos después de 3 intentos vacíos")
                    break

                pagina += 1
                continue

            intentos_vacios = 0

            for producto in productos:
                try:
                    # VARIABLES BASICAS
                    product_id = producto.get('productId', 'NA')
                    titulo = producto.get('productName', 'NA')
                    marca = producto.get('brand', 'NA')
                    descripcion = producto.get('description', 'NA')


                    # CONTENIDO ITEMS (variaciones del producto)
                    items = producto.get('items', [])

                    if items:
                        for item in items:
                            # SKU
                            sku = extraer_sku_correcto(item)

                            # SI PRODUCTO ESTA REPETIDO EN LA CATEGORIA A BUSCAR NO LO CONSIDERA
                            if sku in skus_vistos_en_categoria:
                                continue

                            skus_vistos_en_categoria.add(sku)

                            # NOMBRE
                            nombre_item = item.get('name', titulo)

                            # VENDEDOR
                            sellers = item.get('sellers', [])

                            # CONDICIONAL SI VENDEDOR HA HECHO VENTAS REDUCIR STOCK
                            if sellers:
                                seller = sellers[0]
                                oferta = seller.get('commertialOffer', {})

                                # PRECIO Y STOCK
                                precio = oferta.get('Price', 0)
                                precio_lista = oferta.get('ListPrice', 0)
                                stock = oferta.get('AvailableQuantity', 0)

                                # IMAGEN
                                imagenes = item.get('images', [])
                                imagen = imagenes[0].get('imageUrl', 'NA') if imagenes else 'NA'

                                # EAN <<<<<<<CODIGO DE BARRAS>>>>>>>
                                ean = item.get('ean', 'NA')

                                # COLUMNAS DEL CSV
                                data.append({
                                    'Categoria': categoria_nombre,
                                    'Marca': marca,
                                    'Titulo': nombre_item,
                                    'Descripción': descripcion,
                                    'Product_ID': product_id,
                                    'SKU': sku,
                                    'Código Proovedor': ean,
                                    'Stock': stock,
                                    'Precio': f"${precio:,.0f}" if precio > 0 else 'Sin precio',
                                    'Precio_lista': f"${precio_lista:,.0f}" if precio_lista > 0 else "Sin precio",
                                    'Imagen': imagen,
                                    'URL': f"https://www.ferreteriamarsella.cl{producto.get('link', '')}",
                                })
                    else:
                        # PRODUCTO SIN ITEMS
                        data.append({
                            'Categoria': categoria_nombre,
                            'Marca': marca,
                            'Titulo': titulo,
                            'Descripción': 'Sin descripcion',
                            'Product_ID': 'NA',
                            'SKU': 'N/A',
                            'Código Proovedor': 'NA',
                            'Stock': 'Sin stock',
                            'Precio': 'Sin precio',
                            'Precio_Lista': 'Sin precio',
                            'Imagen': 'N/A',
                            'URL': f"https://www.ferreteriamarsella.cl{producto.get('link', '')}",
                        })

                except Exception as e:
                    print(f" ❌ Error procesando producto: {e}")
                    continue

            print(f" Página {pagina + 1}: {len(productos)} productos | Acumulado: {len(data)}")
            pagina += 1
            time.sleep(.5)

        except Exception as e:
            print(f" ❌ Error en request: {e}")
            break

    return data

def extraer_sku_correcto(item):
    """
    Extraer SKU desde referenceId
    """
    referencias = item.get('referenceId', [])

    # Si tiene referenceId con valor
    if referencias and len(referencias) > 0:
        # Tomar el primer referenceId
        ref = referencias[0]
        sku = ref.get('Value', '')

        if sku:  # Si tiene valor
            return sku

    # Fallback: usar itemId si no hay referenceId
    return item.get('itemId', 'N/A')

# ========================================
# EJECUCIÓN PRINCIPAL
# ========================================

print("\n" + "=" * 70)
print("SCRAPING COMPLETO DE FERRETERIA MARSELLA VÍA API VTEX")
print("=" * 70 + "\n")

print("Obteniendo lista de categorías...\n")
url_categorias = obtener_todas_las_categorias()

if not url_categorias:

    # EN CASO DE ERROR: LISTA MANUAL DE USO

    print("Usando lista manual de categorias \n")

    url_categorias = {
        'construccion_ferreteria': 'https://www.ferreteriamarsella.cl/construccion-y-ferreteria',
        'electricidad': 'https://www.ferreteriamarsella.cl/electricidad',
        'jardineria_aire_libre': 'https://www.ferreteriamarsella.cl/jardineria-aire-libre',
        'herramientas_maquinarias': 'https://www.ferreteriamarsella.cl/herramientas-y-maquinarias',
        'hogar_climatizacion': 'https://www.ferreteriamarsella.cl/hogar-y-climatizacion',
        'limpieza_aseo_industrial': 'https://www.ferreteriamarsella.cl/limpieza-y-aseo-industrial',
        'pinturas_terminaciones': 'https://www.ferreteriamarsella.cl/pinturas-y-terminaciones',
        'soldadoras_complementos': 'https://www.ferreteriamarsella.cl/soldadoras-y-complementos',
        'transporte_carga': 'https://www.ferreteriamarsella.cl/transporte-y-carga'
    }

print(f"Total de categorias a scrapear: {len(url_categorias)}\n")

todos_los_datos = []

for i, (categoria, url) in enumerate(url_categorias.items(), 1):
    print(f"\n[{i}/{len(url_categorias)}] {categoria.upper()}")
    print(f"URL: {url}")

    datos_categoria = scrap_marsella_api(url, categoria)
    todos_los_datos.extend(datos_categoria)

    print(f"✓ {len(datos_categoria)} productos scrapeados de {categoria}")
    print("-" * 70)


df = pd.DataFrame(todos_los_datos)
df.to_csv('scrapping_Marsella.csv', index=False, encoding='utf-8-sig')

print("\n" + "=" * 70)
print(f"✓ SCRAPING COMPLETADO")
print(f"✓ Total productos: {len(todos_los_datos)}")
print(f"✓ Con stock: {len(df[df['Stock'] > 0])}")
print(f"✓ Sin stock: {len(df[df['Stock'] == 0])}")
print(f"✓ Archivo: scrapping_Marsella.csv")
print("=" * 70 + "\n")
