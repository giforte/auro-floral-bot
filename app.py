import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/register", methods=["GET"])
def register_number():
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/register"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "pin": "000000"}
    response = requests.post(url, headers=headers, json=payload)
    return jsonify(response.json())

VERIFY_TOKEN = "auro_floral_token"
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

def send_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    response = requests.post(url, headers=headers, json=payload)
    print(f"STATUS: {response.status_code}")
    print(f"RESPONSE: {response.text}")

def get_response(message, state):
    msg = message.strip().lower()

    if state == "inicio" or msg in ["hola", "buenas", "hi", "hello"]:
        return ("Hola, bienvenida a Auro Floral 🌸\n\nSoy tu asistente virtual. ¿Qué tipo de boda estás planeando?\n\n1️⃣ Ceremonia grande\n2️⃣ Civil\n3️⃣ Íntima", "tipo_boda")

    if state == "tipo_boda":
        return ("¡Qué ilusión! ¿Qué estilo de ramo te imaginas?\n\n1️⃣ Romántico\n2️⃣ Silvestre\n3️⃣ Minimalista", "estilo")

    if state == "estilo":
        return ("Perfecto 💐 ¿Para cuándo es tu boda? Dinos el mes y año aproximado.", "fecha")

    if state == "fecha":
        return ("¡Apuntado! Por último, ¿cuál es tu nombre y tu email para que podamos contactarte?", "contacto")

    if state == "contacto":
        return ("Muchas gracias 🌸 Hemos recibido tus datos y nos pondremos en contacto contigo por email muy pronto.\n\nSi lo prefieres, también puedes visitarnos en tienda. ¡Hasta pronto!", "fin")

    return ("Perdona, no te he entendido bien. Escribe *hola* para empezar de nuevo 😊", state)

conversaciones = {}

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Token incorrecto", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        message = entry["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        state = conversaciones.get(from_number, "inicio")
        respuesta, nuevo_estado = get_response(text, state)
        conversaciones[from_number] = nuevo_estado

        send_message(from_number, respuesta)
    except:
        pass
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
