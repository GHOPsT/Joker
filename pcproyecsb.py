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

            for w in workers:
                w.start()
            for w in workers:
                w.join()

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

if __name__ == '__main__':
    url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    
    start_time = time.time()
    descarga_paralela(url, 20, '20hiloprueba_final.jpg')
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000000
    print(f'Tiempo de ejecución: {elapsed_time} microsegundos')
