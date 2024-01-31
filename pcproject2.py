from pytube import YouTube
import concurrent.futures

def descargar_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download()
        print(f"Video descargado: {url}")
    except Exception as e:
        print(f"Error al descargar el video: {url}. Error: {str(e)}")

urls_videos = ["https://www.youtube.com/watch?v=ALM--Jeb-6c&list=RDALM--Jeb-6c&start_radio=1", "https://www.youtube.com/watch?v=kgnhgFlUIw0", "https://www.youtube.com/watch?v=0kzLeuBD6U8"]  # Reemplaza esto con las URLs de los videos que deseas descargar

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(descargar_video, urls_videos)
