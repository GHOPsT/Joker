import urllib.request
from multiprocessing import Process, Manager
import time

def descargar(url, orden, rango, frag):
    try:
        print('Obteniendo fragmento {}. Descargando desde byte {} hasta byte {}.'.format(orden, *rango))
        req = urllib.request.Request(url)
        req.add_header('Range', 'bytes={}-{}'.format(*rango))
        data = urllib.request.urlopen(req).read()
        if data:
            frag[orden] = data
            print('Fragmento {} descargado correctamente. Obtenidos {} bytes.'.format(orden, len(data)))
        else:
            frag[orden] = None
    except:
        frag[orden] = '#Error'
        raise

def descarga_paralela(url, fragmentos, nombre):
    ranges = None
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
            # Lanzamos los procesos
            workers = [Process(target=descargar, args=(url, i, r, d)) for i, r in enumerate(ranges)]

            # Medir el tiempo de inicio
            start_time = time.time()

            for w in workers:
                w.start()
            for w in workers:
                w.join()

            # Medir el tiempo de finalización
            end_time = time.time()

            # Reconstruimos el archivo usando cada fragmento en su orden correcto:
            with open(nombre, 'wb') as f:
                for i in range(fragmentos):
                    data = d[i]
                    if data == None or data == '#Error':
                        print('El fragmento {} no se puedo descargar. No se puede reconstruir el archivo'.format(i))
                        break
                    else:
                        f.write(data)
                else:
                    print('Archivo descargado y reconstruido con éxito.')

            # Calcular y mostrar el tiempo total de ejecución
            total_time = end_time - start_time
            print('Tiempo total de ejecución: {:.2f} segundos'.format(total_time))

if __name__ == '__main__':
    url = 'https://static.wikia.nocookie.net/typemoon/images/9/98/Caster_Anastasia_FGO_1.png/revision/latest?cb=20210402194132&path-prefix=es'
    descarga_paralela(url, 10, 'imagen1.jpg')