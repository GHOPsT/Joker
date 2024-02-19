from imagekitio import ImageKit
from base64 import b64encode
from pprint import pprint

IK_PUBLIC = "public_JCVYuD+GYX4bjtK7ffiyCMThAeU="
IK_PRIVATE = "private_FzcJdbiv48KjRDyq9M0g13uWKUA="
IK_URL = "https://ik.imagekit.io/ProgramacionParalela"

# Instanciamos ImageKit
ik = ImageKit(public_key=IK_PUBLIC, private_key=IK_PRIVATE, url_endpoint=IK_URL)

def ik_subir_imagen(ruta_imagen, nombre_archivo):
    with open(ruta_imagen, "rb") as f:
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
    res = ik_subir_imagen("C:/Users/Esther Nehisbell/Downloads/photo.jpg", "photo.jpg")
    pprint(res, sort_dicts=False)











