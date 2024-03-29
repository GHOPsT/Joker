from threads import descarga_paralela
from imagekit_api import ik_subir_imagen, delete_image
from flask import Flask, jsonify, request
from heyoo import WhatsApp
import json

app = Flask(__name__)

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
    "descargar": "Descargando el archivo desde {} con {} fragmentos y guardándolo como {}"
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

def enviar_imagen(telefono_recibe, url_imagen):
    token='EAANA5n8mCIYBOZBdxufhy1ZBIKTFTt2vUtTBdyFtBf6toPevdpn1rnLCA5XgLvQvfTDfPSjCbcV8IPkFtn6C8BUniCYyBnEspLT1GUzg3Lc1bk2BQVUHxdZCFhFPjICYiIzhKcBwBrNAWzY6vl65uOvNmM4N4uvZCQZB63L6kslZCZCBeaRudGNSRxtI503dSTscvL2EG6sBDSNVyoUcS7JiJ0XuUeY7HAvnVUZD'
    id_numero_telefono = '205842575953756'
    mensaje_wa = WhatsApp(token, id_numero_telefono)
    telefono_recibe = telefono_recibe.replace("521", "52")
    # Enviamos la URL de la imagen como un mensaje de texto
    mensaje_wa.send_message(url_imagen, telefono_recibe)
    mensaje_wa.send_image(image=url_imagen, recipient_id=telefono_recibe)


def enviar(telefonoRecibe,respuesta):
    #TOKEN DE ACCESO DE FACEBOOK
    token='EAANA5n8mCIYBOZBdxufhy1ZBIKTFTt2vUtTBdyFtBf6toPevdpn1rnLCA5XgLvQvfTDfPSjCbcV8IPkFtn6C8BUniCYyBnEspLT1GUzg3Lc1bk2BQVUHxdZCFhFPjICYiIzhKcBwBrNAWzY6vl65uOvNmM4N4uvZCQZB63L6kslZCZCBeaRudGNSRxtI503dSTscvL2EG6sBDSNVyoUcS7JiJ0XuUeY7HAvnVUZD'
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