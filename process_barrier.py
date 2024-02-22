import urllib.request
import os
from multiprocessing import Process, Manager, Barrier, Lock
import time

def descargar(url, orden, rango, frag, barrier, lock, retry_limit=3):
    try:
        print('Obteniendo fragmento {}. Descargando desde byte {} hasta byte {}.'.format(orden, *rango))
        req = urllib.request.Request(url)
        req.add_header('Range', 'bytes={}-{}'.format(*rango))

        for _ in range(retry_limit):
            try:
                with lock:  # Utiliza el bloqueo del Manager directamente
                    data = urllib.request.urlopen(req).read()
                if data:
                    with lock:
                        frag[orden] = data
                    print('Fragmento {} descargado correctamente. Obtenidos {} bytes.'.format(orden, len(data)))
                    break
            except Exception as e:
                print(f'Error al descargar fragmento {orden}: {e}')
        else:
            with lock:
                frag[orden] = '#Error'
    finally:
        barrier.wait()

def descarga_paralela(url, fragmentos, nombre, directorio='images'):
    ranges = None
    try:
        with urllib.request.urlopen(url) as f:
            # Comprobamos que el servidor acepte la descarga parcial.
            if f.getheader("Accept-Ranges", "none").lower() != "bytes":
                print('Descarga parcial no soportada, iniciando descarga...')
            else:
                print('Descarga parcial soportada')

                # Obtenemos el tamaño total del archivo
                size = int(f.getheader("Content-Length", "none"))
                print('Tamaño del archivo: {} bytes.'.format(size))

                # Dividimos ese tamaño en intervalos de acuerdo al número de procesos que lanzaremos
                tamF = size // fragmentos
                print('Fragmentos: {}.\nTamaño aproximado por fragmento: {} bytes.'.format(fragmentos, tamF))
                ranges = [[i, i + tamF - 1] for i in range(0, size, tamF)]
                ranges[-1][-1] = size

                manager = Manager()
                d = manager.dict()

                # Crear una barrera para coordinar los procesos
                barrier = Barrier(fragmentos + 1)

                # Lanzamos los procesos
                workers = [Process(target=descargar, args=(url, i, r, d, barrier, lock)) for i, r in enumerate(ranges)]
                for w in workers:
                    w.start()

                start_time = time.time()

                # Esperar a que todos los procesos completen la descarga antes de continuar
                barrier.wait()

                end_time = time.time()  # Tomamos el tiempo después de que todos los procesos han completado
                elapsed_time = (end_time - start_time) * 1000000
                print(f'Tiempo de ejecución: {elapsed_time} microsegundos')

                # Reconstruimos el archivo usando cada fragmento en su orden correcto:
                ruta_completa = os.path.join(directorio, nombre)
                with open(ruta_completa, 'wb') as f:
                    for i in range(fragmentos):
                        data = d[i]
                        if data is None or data == '#Error':
                            print('El fragmento {} no se pudo descargar. No se puede reconstruir el archivo'.format(i))
                            break
                        else:
                            print(f"El fragmento {i} no está presente en el diccionario compartido.")
                            f.write(data)
                    else:
                        print('Archivo descargado y reconstruido con éxito en el directorio:{ruta_completa}')
                        return ruta_completa
    except urllib.error.URLError as e:
        print(f"Error al abrir la URL: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")

if __name__ == '__main__':
    with Manager() as manager:  # Utiliza el Manager como un contexto para garantizar la limpieza adecuada
        lock = manager.Lock()
        try:
            url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
            descarga_paralela(url, 20, '20_hprueba_final_v2pcb.jpg', directorio='images')
        except Exception as e:
            print(f"Error durante la descarga: {e}")

