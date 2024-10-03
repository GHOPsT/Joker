import os
import time
import requests

# Obtiene la capacidad del servidor
def obtener_capacidad_servidor():
    return os.cpu_count()

# Descarga un fragmento de la URL
def descargar(url, rango):
    headers = {'Range': 'bytes={}-{}'.format(*rango)}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except Exception as e:
        manejar_errores(e, f'descarga de fragmento {rango}')
        return None

# Verifica si la descarga parcial es soportada
def verificar_soporte_descarga_parcial(response):
    if 'Accept-Ranges' not in response.headers or response.headers['Accept-Ranges'].lower() != 'bytes':
        raise ValueError("Descarga parcial no soportada")
    print('Descarga parcial soportada')

# Obtiene los rangos de descarga basados en el tamaño total del archivo y la cantidad de fragmentos
def obtener_rangos_descarga(size, fragmentos):
    tamF = size // fragmentos
    ranges = [(i, i + tamF - 1) for i in range(0, size, tamF)]
    ranges[-1] = (ranges[-1][0], size - 1)  # Ajuste final
    return ranges

# Maneja la reconstrucción de los fragmentos en un archivo
def manejar_fragmentos(fragmentos_descargados, directorio, nombre):
    ruta_completa = os.path.join(directorio, nombre)
    with open(ruta_completa, 'wb') as file:
        for data in fragmentos_descargados:
            if data is None:
                raise IOError("Error en fragmentos, no se pudo reconstruir el archivo.")
            file.write(data)
    print(f'Archivo descargado y reconstruido con éxito en: {ruta_completa}')

# Centraliza el manejo de errores
def manejar_errores(e, contexto):
    print(f"Error en {contexto}: {e}")

# Descarga los fragmentos secuencialmente
def descargar_fragmentos_secuencial(url, ranges):
    fragmentos_descargados = []
    for i, rango in enumerate(ranges):
        data = descargar(url, rango)
        fragmentos_descargados.append(data)
        if data is None:
            manejar_errores(Exception(f"Fragmento {i} fallido"), f"descarga de fragmento {i}")
            break
    return fragmentos_descargados

# Descarga secuencial completa
def descarga_secuencial(url, fragmentos, nombre, directorio='images'):
    try:
        with requests.get(url, stream=True) as response:
            verificar_soporte_descarga_parcial(response)

            size = int(response.headers.get("Content-Length", "0"))
            print(f'Tamaño del archivo: {size} bytes.')

            ranges = obtener_rangos_descarga(size, fragmentos)

            # Inicia el temporizador
            start_time = time.perf_counter()

            # Descargar los fragmentos
            fragmentos_descargados = descargar_fragmentos_secuencial(url, ranges)

            # Manejar los fragmentos descargados
            manejar_fragmentos(fragmentos_descargados, directorio, nombre)

            # Detiene el temporizador
            end_time = time.perf_counter()
            elapsed_time = (end_time - start_time) * 1000000
            print(f'Tiempo de ejecución (parte secuencial): {elapsed_time} microsegundos')

    except requests.exceptions.RequestException as e:
        manejar_errores(e, "apertura de la URL")
    except Exception as e:
        manejar_errores(e, "descarga secuencial")

# Bloque principal
if __name__ == '__main__':
    try:
        url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
        # Obtener la capacidad del servidor
        capacidad_servidor = obtener_capacidad_servidor()
        print(f"Capacidad del servidor: {capacidad_servidor} núcleos de CPU")
        descarga_secuencial(url, capacidad_servidor, 'descarga_secuencial.jpg', directorio='images')
    except Exception as e:
        manejar_errores(e, "bloque principal")
