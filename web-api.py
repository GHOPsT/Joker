from pcproject import descarga_paralela
from flask import Flask, jsonify, request
from heyoo import WhatsApp
import os
app = Flask(__name__)

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
                ruta_imagen = os.path.join("images", nombre)
                enviar_imagen(telefonoRecibe, ruta_imagen)
                return formato_respuesta.format(url, fragmentos, nombre)  # Aquí debes implementar la lógica para obtener la respuesta del comando
            
    # Si no hay coincidencia con palabras clave, devuelve None
    return None

def enviar_imagen(telefono_recibe, ruta_imagen):
    token = 'EAANA5n8mCIYBO4WHwrMguHCZCZAb55h3goDpqazIMyA0Iya6zjcHEkvA0l1iGUNVOCoK4Pf3pRVzxOpZCTCMYBZCWP3pEmGLTZBx2jZCCdDBexp688uBXgm8LJ3eNXmU0Yya5DbTh0s50NEvP74mA1hoLeJHgnOPhtS1w4sh8KxHWJnlzwa6YORPNr8EzEWam0dcakL0hZCWZCMEi8lYGSZCTlC9TJUwWRA0OYKQZD'
    id_numero_telefono = '205842575953756'
    mensaje_wa = WhatsApp(token, id_numero_telefono)
    telefono_recibe = telefono_recibe.replace("521", "52")
    mensaje_wa.send_image(image=ruta_imagen, recipient_id=telefono_recibe)

def enviar(telefonoRecibe,respuesta):
    #TOKEN DE ACCESO DE FACEBOOK
    token='EAANA5n8mCIYBO4WHwrMguHCZCZAb55h3goDpqazIMyA0Iya6zjcHEkvA0l1iGUNVOCoK4Pf3pRVzxOpZCTCMYBZCWP3pEmGLTZBx2jZCCdDBexp688uBXgm8LJ3eNXmU0Yya5DbTh0s50NEvP74mA1hoLeJHgnOPhtS1w4sh8KxHWJnlzwa6YORPNr8EzEWam0dcakL0hZCWZCMEi8lYGSZCTlC9TJUwWRA0OYKQZD'
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
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)