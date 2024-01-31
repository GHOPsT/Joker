from nltk.chat.util import Chat, reflections

pares = [
    [
        r"mi nombre es (.*)",
        ["Hola %1, ¿cómo estás?",]
    ],
    [
        r"¿cuál es tu nombre ?",
        ["Mi nombre es Chatbot.",]
    ],
    [
        r"¿cómo estás ?",
        ["Bien, ¿y tú?",]
    ],
    [
        r"disculpa (.*)",
        ["No pasa nada.",]
    ],
    [
        r"hola|hey|buenas",
        ["Hola", "¿Qué tal?",]
    ],
    [
        r"¿qué (.*) quieres ?",
        ["Nada, gracias.",]
    ],
    [
        r"¿(.*) creado ?",
        ["Fui creado hoy.",]
    ],
    [
        r"finalizar",
        ["Chao","Fue bueno hablar contigo."]
    ],
]

def chatear():
    print("Hola, soy un bot. Escribe algo para comenzar.")
    chat = Chat(pares, reflections)
    chat.converse()

if __name__ == "__main__":
    chatear()
