from imagekitio import ImageKit
from base64 import b64encode
from pprint import pprint
import os

IK_PUBLIC = "public_JCVYuD+GYX4bjtK7ffiyCMThAeU="
IK_PRIVATE = "private_FzcJdbiv48KjRDyq9M0g13uWKUA="
IK_URL = "https://ik.imagekit.io/ProgramacionParalela"

RUTA_POR_DEFECTO = r"C:\Users\GHOST\OneDrive\Escritorio\Joker\images"

# Instanciamos ImageKit
ik = ImageKit(public_key=IK_PUBLIC, private_key=IK_PRIVATE, url_endpoint=IK_URL)

def ik_subir_imagen(nombre_archivo):

    ruta_completa = os.path.join(RUTA_POR_DEFECTO,nombre_archivo)
    with open(ruta_completa, "rb") as f:
        imagen = b64encode(f.read())
    print("Subiendo la imagen a ImageKit")
    try:
        res = ik.upload_file(file=imagen, file_name=nombre_archivo)
    except Exception as e:
        return f'ERROR: {e}'
    status_code = res.response_metadata.http_status_code
    if status_code == 200:
        return res.response_metadata.raw
    else:
        return f'ERROR: {status_code}'

if __name__ == '__main__':
    nombre_personalizado = "prueba.jpg"
    res = ik_subir_imagen(nombre_personalizado)
    pprint(res, sort_dicts=False)











