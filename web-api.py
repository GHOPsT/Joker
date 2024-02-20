from pcproject import descarga_paralela # Import descarga_paralela function from pcproject module
from imagekit_api import ik_subir_imagen
from flask import Flask, jsonify, request
from heyoo import WhatsApp
import os
import urllib.request
from multiprocessing import Process, Manager, Barrier, Lock, freeze_support
from imagekitio import  ImageKit
import requests
import json

IK_PUBLIC = "public_kvsihz1+EXedGSE+ZnfbnAo5BpA="
IK_PRIVATE = "private_Mxa6LgyTZPTBrQXH9MaIzir7kqU="
IK_URL = "https://ik.imagekit.io/PPyC"

RUTA_PREDETERMINADA = r"C:\Users\GHOST\OneDrive\Escritorio\Joker\images"

ik = ImageKit(public_key=IK_PUBLIC, private_key=IK_PRIVATE, url_endpoint=IK_URL)

if __name__ == '__main__':
    freeze_support()
    manager = Manager()
    lock = manager.Lock()

app = Flask(__name__)

# ---------------------- Enviar imagenes a apip funcion --------------------------------
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


# ----------------------------- DESCARGA PARALELA FUNCIONES ------------------------------------

def descargar(url, orden, rango, frag, barrier, lock):
    try:
        print(f'Obteniendo fragmento {orden}. Descargando desde byte {rango[0]} hasta byte {rango[1]}.' )
        req = urllib.request.Request(url)
        req.add_header('Range', f'bytes={rango[0]}-{rango[1]}')

        with lock:
            data = urllib.request.urlopen(req).read()
            frag[orden] = data
            print(f'Fragmento {orden} descargado correctamente. Obtenidos {len(data)} bytes.')
    except Exception as e:
        print(f'Error al descargar fragmento {orden}: {e}')
    finally:
        barrier.wait()

def descarga_paralela(url, fragmentos, nombre, directorio='images'):
    ranges = None

    try:
        with urllib.request.urlopen(url) as f:
            if f.getheader("Accept-Ranges", "none").lower() != "bytes":
                print('Descarga parcial no soportada, iniciando descarga...')
            else:
                size = int(f.getheader("Content-Length", "none"))
                print(f'Tamaño del archivo: {size} bytes.')
                tamF = size // fragmentos
                print(f'Fragmentos: {fragmentos}. Tamaño aproximado por fragmento: {tamF} bytes.')
                ranges = [[i, i + tamF - 1] for i in range(0, size, tamF)]
                ranges[-1][-1] = size

                manager = Manager()
                d = manager.dict()

                barrier = Barrier(fragmentos + 1)

                workers = [Process(target=descargar, args=(url, i, r, d, barrier, lock)) for i, r in enumerate(ranges)]

                for w in workers:
                    w.start()

                barrier.wait()

                ruta_completa = os.path.join(directorio, nombre)
                with open(ruta_completa, 'wb') as f:
                    for i in range(fragmentos):
                        data = d.get(i, None)
                        if data is None or data == '#Error':
                            print(f'El fragmento {i} no se pudo descargar. No se puede reconstruir el archivo.')
                            break
                        else:
                            f.write(data)
                    else:
                        print(f'Archivo descargado y reconstruido con éxito en: {ruta_completa}')
                        return ruta_completa
    except urllib.error.URLError as e:
        print(f"Error al abrir la URL: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")

#---------------------------------------------------------------------------------------
# ------------ Biblioteca de Respuestas ------------------------------------------------

# Definir respuestas predeterminadas según palabras clave
respuestas_predeterminadas = {
    "hola": "¡Hola! ¿En qué puedo ayudarte?",
    "adios": "Hasta luego. ¡Que tengas un buen día!",
    "informacion": "Puedo proporcionarte información interesante.",
}
# Definir comandos que requieren una entrada adicional
comandos_con_entrada = {
    "clima": "El clima en {} es: {}",
    "hora": "La hora en {} es: {}",
    "descargar": "Descargando el archivo desde {} con {} fragmentos y guardándolo como {}"
    # Agrega aquí más comandos que requieran una entrada adicional
}

# ---------------------------------------------------------------------------------------
# ---------------------- WEBHOOK - API WHATSAPP ----------------------------

#CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "HolaNovato":
            #ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            #SI NO SON IGUALES RETORNAMOS UN MENSAJE DE ERROR
          return "Error de autentificacion."
    #RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data=request.get_json()
    print(data)
    if 'entry' in data and data['entry'] and 'changes' in data['entry'][0] and data['entry'][0]['changes']:
        message_data = data['entry'][0]['changes'][0]['value']
        #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
        if 'messages' in message_data and message_data['messages']:
            telefono_cliente = message_data['messages'][0].get('from')
            mensaje = message_data['messages'][0].get('text', {}).get('body')
            telefono_recibe = None
            telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            if mensaje is not None:
                telefono_recibe = telefono_cliente.replace("521", "52")
                respuesta = obtener_respuesta_predeterminada(mensaje, telefono_recibe)
                if respuesta:
                    enviar(telefono_cliente, respuesta)
                return jsonify({"status": "success"}, 200)
    return jsonify({"status": "error", "message": "Datos de solicitud no válidos"}, 400)

# ------------------------------------------------------------------------------
# ---------------- RECIBO DE RESPUESTAS  ------------------------------------

def obtener_respuesta_predeterminada(mensaje, telefonoRecibe):
    # Convertir el mensaje a minúsculas para hacer la comparación sin distinción de mayúsculas y minúsculas
    mensaje = mensaje.lower()

    if telefonoRecibe is not None:
        telefonoRecibe = telefonoRecibe.replace("521","52")

    for palabra_clave, respuesta in respuestas_predeterminadas.items():
        if palabra_clave in mensaje:
            return respuesta
        
    for comando, formato_respuesta in comandos_con_entrada.items():
        if comando in mensaje:
            entrada = mensaje.replace(comando, '').strip()  # Obtener la entrada adicional
            if comando == "descargar":
                url, fragmentos, nombre = entrada.split()  # Aquí asumimos que la entrada adicional son tres valores separados por espacios
                descarga_paralela(url, int(fragmentos), nombre, directorio='images')  # Aquí debes implementar la lógica para descargar el archivo
                if nombre is not None:
                    respuesta = ik_subir_imagen(nombre)
                    if isinstance(respuesta, dict):
                        respuesta_dict = respuesta
                    else:
                        respuesta_dict = json.loads(respuesta)
                    url_imagen = respuesta_dict['url']
                    enviar_imagen(telefonoRecibe, url_imagen)
                return formato_respuesta.format(url, fragmentos, nombre)  # Aquí debes implementar la lógica para obtener la respuesta del comando
            else:
                return "Error al descargar la imagen. Verifique el enlace e intentelo de nuevo. "
            
    # Si no hay coincidencia con palabras clave, devuelve None
    return None

# -------------------------------------------------------------------
# ------------------ ENVIO DE RESPUESTAS ----------------------------------------

def enviar_imagen(telefono_recibe, ruta_imagen):
    token = 'EAANA5n8mCIYBO7uRJNCWKgJbubFNCFjB2TlA2noxZA2LL05vxmA3QAEAOPsSnlTcRkaKlDW3UxjvWEnm7CeZBHFcbDuAuRStxRGw2ZBemTK4pJvCzrzhJRCOob34PKShXJtF0DKDiRS1c0dZCcSQBcqLOWmc8Nzl027pKYa2rzrql4mvSaFwn6FMw3QnONjQZCVqATgQXqqIBO21R9DhYyahyxlMoUWiucSJa'
    id_numero_telefono = '205842575953756'
    mensaje_wa = WhatsApp(token, id_numero_telefono)
    telefono_recibe = telefono_recibe.replace("521", "52")
    # Llamamos a la función ik_subir_imagen_url y obtenemos la respuesta
    respuesta_ik = ik_subir_imagen(ruta_imagen)
    # Procesamos la respuesta de ik_subir_imagen_url, que es una cadena JSON
    try:
        respuesta_dict = eval(respuesta_ik)
        url_imagen = respuesta_dict.get('url', 'URL no disponible')
    except (TypeError, SyntaxError):
        url_imagen = 'URL no disponible'
    # Enviamos la imagen con la URL obtenida
    mensaje_wa.send_image(image=url_imagen, recipient_id=telefono_recibe)


def enviar(telefonoRecibe,respuesta):
    #TOKEN DE ACCESO DE FACEBOOK
    token='EAANA5n8mCIYBO7uRJNCWKgJbubFNCFjB2TlA2noxZA2LL05vxmA3QAEAOPsSnlTcRkaKlDW3UxjvWEnm7CeZBHFcbDuAuRStxRGw2ZBemTK4pJvCzrzhJRCOob34PKShXJtF0DKDiRS1c0dZCcSQBcqLOWmc8Nzl027pKYa2rzrql4mvSaFwn6FMw3QnONjQZCVqATgQXqqIBO21R9DhYyahyxlMoUWiucSJa'
    #IDENTIFICADOR DE NÚMERO DE TELÉFONO
    idNumeroTeléfono='205842575953756'
    #INICIALIZAMOS ENVIO DE MENSAJES
    mensajeWa=WhatsApp(token,idNumeroTeléfono)

    if telefonoRecibe is not None:
        telefonoRecibe = telefonoRecibe.replace("521", "52")
        # ENVIAMOS UN MENSAJE DE TEXTO
        mensajeWa.send_message(respuesta, telefonoRecibe)
    else:
        print("Error: No se pudo determinar el número de teléfono del destinatario.")

#INICIAMOS FLASK
if __name__ == "__main__":
    app.run(debug=True)