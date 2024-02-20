import urllib.request
import os
import time
import threading

def descargar(url, rango, frag, lock, retry_limit=3):
        print('Descargando desde byte {} hasta byte {}.'.format(*rango))
        req = urllib.request.Request(url)
        req.add_header('Range', 'bytes={}-{}'.format(*rango))

        for _ in range(retry_limit):
            try:
                with lock:
                    data = urllib.request.urlopen(req).read()
                if data:
                    with lock:
                        frag.append(data)
                    print('Fragmento descargado correctamente. Obtenidos {} bytes.'.format(len(data)))
                    break
            except Exception as e:
                print(f'Error al descargar fragmento: {e}')
        else:
            with lock:
                frag.append('#Error')

def descarga_secuencial(url, fragmentos, nombre, directorio='images'):
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
                ranges = [[i * tamF, (i + 1) * tamF - 1] for i in range(fragmentos)]

                lock = threading.Lock()
                frag = []

                for r in ranges:
                    descargar(url, r, frag, lock)

                # Reconstruimos el archivo usando cada fragmento en su orden correcto:
                ruta_completa = os.path.join(directorio, nombre)
                with open(ruta_completa, 'wb') as f:
                    for data in frag:
                        if data == '#Error':
                            print('Un fragmento no se pudo descargar. No se puede reconstruir el archivo.')
                            break
                        else:
                            f.write(data)
                    else:
                        print('Archivo descargado y reconstruido con éxito en el directorio: {}'.format(ruta_completa))
                        return ruta_completa
    except urllib.error.URLError as e:
        print(f"Error al abrir la URL: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")

if __name__ == '__main__':
    try:
        url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
        start_time = time.time()
        descarga_secuencial(url, 20, '20hilospruebafinal_SC.jpg', directorio='images')
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000000
        print(f'Tiempo de ejecución: {elapsed_time} microsegundos')
    except Exception as e:
        print(f"Error durante la descarga: {e}")
