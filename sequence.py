import os
import time
import requests

def obtener_capacidad_servidor():
    return os.cpu_count()

def descargar(url, rango):
    headers = {'Range': 'bytes={}-{}'.format(*rango)}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f'Error al descargar fragmento {rango}: {e}')
        return None

def descarga_secuencial(url, fragmentos, nombre, directorio='images'):
    try:
        with requests.get(url, stream=True) as response:
            if 'Accept-Ranges' not in response.headers or response.headers['Accept-Ranges'].lower() != 'bytes':
                print('Descarga parcial no soportada, iniciando descarga...')
            else:
                print('Descarga parcial soportada')

                size = int(response.headers.get("Content-Length", "0"))
                print('Tamaño del archivo: {} bytes.'.format(size))

                tamF = size // fragmentos
                print('Fragmentos: {}.\nTamaño aproximado por fragmento: {} bytes.'.format(fragmentos, tamF))
                ranges = [(i, i + tamF - 1) for i in range(0, size, tamF)]
                ranges[-1] = (ranges[-1][0], size - 1)

                # Inicia el temporizador para la parte secuencial
                start_time = time.perf_counter()

                fragmentos_descargados = []
                for i, rango in enumerate(ranges):
                    data = descargar(url, rango)
                    fragmentos_descargados.append(data)
                    if data is None:
                        print('El fragmento {} no se pudo descargar. No se puede reconstruir el archivo'.format(i))
                        break
                    else:
                        print(f"El fragmento {i} no está presente en el diccionario compartido.")

                # Detiene el temporizador para la parte secuencial
                end_time = time.perf_counter()
                elapsed_time = (end_time - start_time) * 1000000

                ruta_completa = os.path.join(directorio, nombre)
                with open(ruta_completa, 'wb') as file:
                    for i, data in enumerate(fragmentos_descargados):
                        if data is None:
                            break
                        file.write(data)

                # Imprime el tiempo de ejecución de la parte secuencial
                print(f'Tiempo de ejecución (parte secuencial): {elapsed_time} microsegundos')

    except requests.exceptions.RequestException as e:
        print(f"Error al abrir la URL: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")

if __name__ == '__main__':
    try:
        url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
        # Obtener la capacidad del servidor
        capacidad_servidor = obtener_capacidad_servidor()
        print(f"Capacidad del servidor: {capacidad_servidor} núcleos de CPU")
        descarga_secuencial(url, capacidad_servidor, 'descarga_secuencial.jpg', directorio='images')
    except Exception as e:
        print(f"Error durante la descarga: {e}")
