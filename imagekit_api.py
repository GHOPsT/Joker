from imagekitio import ImageKit
from pprint import pprint
import requests
import os

IK_PUBLIC = "public_kvsihz1+EXedGSE+ZnfbnAo5BpA="
IK_PRIVATE = "private_Mxa6LgyTZPTBrQXH9MaIzir7kqU="
IK_URL = "https://ik.imagekit.io/PPyC"

ik = ImageKit(public_key=IK_PUBLIC, private_key=IK_PRIVATE, url_endpoint=IK_URL)

def ik_subir_imagen_desde_url(url, nombre_archivo):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Subiendo la imagen a ImageKit...")
            res = ik.upload_file(file=response.content, file_name=nombre_archivo)
            status_code = res.response_metadata.http_status_code
            if status_code == 200:
                return res.response_metadata.raw
            else:
                return f'ERROR: {status_code}'
        else:
            return f'ERROR: No se pudo descargar la imagen desde la URL. Código de estado: {response.status_code}'
    except Exception as e:
        return f'ERROR: {e}'
    
def ik_subir_imagen_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Subiendo la imagen a ImageKit...")
            res = ik.upload_file(file=response.content, file_name="imagen_api.jpg")
            status_code = res.response_metadata.http_status_code
            if status_code == 200:
                return res.response_metadata.raw
            else:
                return f'ERROR: {status_code}'
        else:
            return f'ERROR: No se pudo descargar la imagen desde la URL. Código de estado: {response.status_code}'
    except Exception as e:
        return f'ERROR: {e}'
    
def delete_image(file_id):
    try:
        res = ik.delete_file(file_id=file_id)
    except Exception as e:
        return f'ERROR: {e.message}'
    status_code = res.response_metadata.http_status_code
    if status_code == 204:
        return "OK"
    else:
        return f'ERROR: {status_code}'

if __name__ == '__main__':
    #url = 'https://images.unsplash.com/photo-1703179159632-d5c6842a1cf2?q=80&w=1376&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    #res = ik_subir_imagen_desde_url(url, "imagen_desde_url.jpg")
    #pprint(res, sort_dicts=False)
    res = delete_image("65d29f8288c257da33bf1c19")
    print(res)












