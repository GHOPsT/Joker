import urllib.request
import os
import time

def descargar(url, nombre, directorio='images', retry_limit=3):
    try:
        print('Descargando archivo desde {}'.format(url))
        start_time = time.time()
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = response.read()
            if data:
                ruta_completa = os.path.join(directorio, nombre)
                with open(ruta_completa, 'wb') as f:
                    f.write(data)
                end_time = time.time()  # Medir el tiempo de fin de la descarga
                elapsed_time = (end_time - start_time)
                print('Archivo descargado y guardado con éxito en el directorio: {}'.format(ruta_completa))
                print(f'Tiempo de descarga: {elapsed_time} microsegundos')
            else:
                print('Error: No se pudo obtener datos del servidor.')
    except Exception as e:
        print('Error durante la descarga: {}'.format(e))

if __name__ == '__main__':
    try:
        url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
        start_time = time.time()
        descargar(url, 'prueba_final_secuencial_Sinhilosnweimage.jpg', directorio='images')
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000000
        print(f'Tiempo de ejecución: {elapsed_time} microsegundos')
    except Exception as e:
        print(f"Error durante la descarga: {e}")
