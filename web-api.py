#Código de Recibir WhatsApp y crear una respuesta con ChatGPT
from flask import Flask, jsonify, request
app = Flask(__name__)

# Definir respuestas predeterminadas según palabras clave
respuestas_predeterminadas = {
    "hola": "¡Hola! ¿En qué puedo ayudarte?",
    "adios": "Hasta luego. ¡Que tengas un buen día!",
    "informacion": "Puedo proporcionarte información interesante.",
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
    #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
    telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    #EXTRAEMOS EL TELEFONO DEL CLIENTE
    mensaje=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    #SI HAY UN MENSAJE
    if mensaje is not None:
        
        #import openai
        # Indica el API Key
        #openai.api_key = "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"
        # Uso de ChapGPT en Python
        #model_engine = "gpt-3.5-turbo"
        #prompt = mensaje
        #completion = openai.Completion.create(engine=model_engine,
        #                                    prompt=prompt,
        #                                    max_tokens=1024,
        #                                      n=1,
        #                                    stop=None,
        #                                    temperature=0.7)
        
        #respuesta=""
        #for choice in completion.choices:
        #    respuesta=respuesta+choice.text
        #    print(f"Response: %s" % choice.text)
        #respuesta=respuesta.replace("\\n","\\\n")
        #respuesta=respuesta.replace("\\","")
        #f = open("texto.txt", "w")
        #f.write(respuesta)
        #f.close()
        respuesta = obtener_respuesta_predeterminada(mensaje)
        if respuesta:
            enviar(telefonoCliente,respuesta)
        #RETORNAMOS EL STATUS EN UN JSON
        return jsonify({"status": "success"}, 200)
    
def obtener_respuesta_predeterminada(mensaje):
    # Convertir el mensaje a minúsculas para hacer la comparación sin distinción de mayúsculas y minúsculas
    mensaje = mensaje.lower()

    for palabra_clave, respuesta in respuestas_predeterminadas.items():
        if palabra_clave in mensaje:
            return respuesta

    # Si no hay coincidencia con palabras clave, devuelve None
    return None

def enviar(telefonoRecibe,respuesta):
    from heyoo import WhatsApp
    #TOKEN DE ACCESO DE FACEBOOK
    token='EAANA5n8mCIYBO1SPEycs1L0rzXwMrVd8ZAij6l4L0YzZAbm7a9RTNZCSlOMK1sJs7ZAbQAdCJZClQ3vn6WQQg3p3NZBaoDiUkv59F3awmY2vhdONR4ud3zYgGaNMfwwAc5l02K4ZCqW4uNQg1EQvOOHyhZC24oUZARFtiZAw3ZCxphAo0hsZCfsD1h2XEu30IC1SyJmEMFhwUMXZASHDSKF2XEQuPsawjKjN8kGldhG0ZD'
    #IDENTIFICADOR DE NÚMERO DE TELÉFONO
    idNumeroTeléfono='205842575953756'
    #INICIALIZAMOS ENVIO DE MENSAJES
    mensajeWa=WhatsApp(token,idNumeroTeléfono)
    telefonoRecibe=telefonoRecibe.replace("521","52")
    #ENVIAMOS UN MENSAJE DE TEXTO
    mensajeWa.send_message(respuesta,telefonoRecibe)
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)