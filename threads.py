import urllib.request
import os
import threading
import time
import multiprocessing

def obtener_capacidad_servidor():
    cores = multiprocessing.cpu_count()
    return cores

def descargar(url, orden, rango, frag, semaphore, retry_limit=3):
    try:
        print('Obteniendo fragmento {}. Descargando desde byte {} hasta byte {}.'.format(orden, *rango))
        req = urllib.request.Request(url)
        req.add_header('Range', 'bytes={}-{}'.format(*rango))

        for _ in range(retry_limit):
            try:
                data = urllib.request.urlopen(req).read()
                if data:
                    with semaphore:
                        frag[orden] = data
                    print('Fragmento {} descargado correctamente. Obtenidos {} bytes.'.format(orden, len(data)))
                    break
            except Exception as e:
                print(f'Error al descargar fragmento {orden}: {e}')
        else:
            with semaphore:
                frag[orden] = '#Error'

    except Exception as e:
        print(f'Error al descargar fragmento {orden}: {e}')

def descarga_paralela(url, fragmentos, nombre, directorio='images'):
    ranges = None
    try:
        with urllib.request.urlopen(url) as f:
            if f.getheader("Accept-Ranges", "none").lower() != "bytes":
                print('Descarga parcial no soportada, iniciando descarga...')
            else:
                print('Descarga parcial soportada')

                size = int(f.getheader("Content-Length", "none"))
                print('Tamaño del archivo: {} bytes.'.format(size))

                tamF = size // fragmentos
                print('Fragmentos: {}.\nTamaño aproximado por fragmento: {} bytes.'.format(fragmentos, tamF))
                ranges = [[i, i + tamF - 1] for i in range(0, size, tamF)]
                ranges[-1][-1] = size

                frag = [None] * len(ranges)  # Definir frag con la longitud real de fragmentos
                semaphore = threading.Semaphore()

                # Inicia el temporizador para la parte paralela
                start_time = time.perf_counter()

                threads = [threading.Thread(target=descargar, args=(url, i, r, frag, semaphore)) for i, r in enumerate(ranges)]
                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                # Detiene el temporizador para la parte paralela
                end_time = time.perf_counter()
                elapsed_time = (end_time - start_time) * 1000000

                ruta_completa = os.path.join(directorio, nombre)
                with open(ruta_completa, 'wb') as file:
                    for i in range(len(frag)):
                        data = frag[i]
                        if data is None or data == '#Error':
                            print('El fragmento {} no se pudo descargar. No se puede reconstruir el archivo'.format(i))
                            break
                        else:
                            print(f"El fragmento {i} no está presente en el diccionario compartido.")
                            file.write(data)
                    else:
                        print('Archivo descargado y reconstruido con éxito en el directorio: {}'.format(ruta_completa))

                # Imprime el tiempo de ejecución de la parte paralela
                print(f'Tiempo de ejecución (parte paralela): {elapsed_time} microsegundos')

    except urllib.error.URLError as e:
        print(f"Error al abrir la URL: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")

if __name__ == '__main__':
    try:
        url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
        # Obtener la capacidad del servidor
        capacidad_servidor = obtener_capacidad_servidor()
        print(f"Capacidad del servidor: {capacidad_servidor} núcleos de CPU")
        descarga_paralela(url, capacidad_servidor, '12_hilosprueba_final_pcbnewimagev3.jpg', directorio='images')
    except Exception as e:
        print(f"Error durante la descarga: {e}")
