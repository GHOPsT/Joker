import urllib.request
from multiprocessing import Process, Manager
from pytube import YouTube
import concurrent.futures
import tkinter as tk
from tkinter import messagebox

def descargar(url, orden, rango, frag):
    try:
        req = urllib.request.Request(url)
        req.add_header('Range', 'bytes={}-{}'.format(*rango))
        data = urllib.request.urlopen(req).read()
        if data:
            frag[orden] = data
        else:
            frag[orden] = None
    except:
        frag[orden] = '#Error'
        raise

def descarga_paralela(url, fragmentos, nombre):
    ranges = None
    with urllib.request.urlopen(url) as f:
        if f.getheader("Accept-Ranges", "none").lower() != "bytes":
            print('Descarga parcial no soportada, iniciando descarga...')
        else:
            size = int(f.getheader("Content-Length", "none"))
            tamF = size // fragmentos
            ranges = [[i, i + tamF - 1] for i in range(0, size, tamF)]
            ranges[-1][-1] = size

            manager = Manager()
            d = manager.dict()
            workers = [Process(target=descargar, args=(url, i, r, d)) for i, r in enumerate(ranges)]
            for w in workers:
                w.start()
            for w in workers:
                w.join()

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

def descargar_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download()
        print(f"Video descargado: {url}")
    except Exception as e:
        print(f"Error al descargar el video: {url}. Error: {str(e)}")

def descargar_videos(urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(descargar_video, urls)

def iniciar_descarga():
    url_imagen = url_imagen_entry.get()
    url_videos = url_videos_entry.get().split(',')
    descarga_paralela(url_imagen, 10, 'imagen.jpg')
    descargar_videos(url_videos)
    messagebox.showinfo("Descarga", "La descarga ha comenzado.")

root = tk.Tk()
root.title("Descargador")

url_imagen_label = tk.Label(root, text="URL de la imagen:")
url_imagen_label.pack()
url_imagen_entry = tk.Entry(root)
url_imagen_entry.pack()

url_videos_label = tk.Label(root, text="URLs de los videos (separadas por comas):")
url_videos_label.pack()
url_videos_entry = tk.Entry(root)
url_videos_entry.pack()

descargar_button = tk.Button(root, text="Descargar", command=iniciar_descarga)
descargar_button.pack()

root.mainloop()
