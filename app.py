from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Webhook verification token
VERIFY_TOKEN = "nomadller123"

# Your credentials from Meta
ACCESS_TOKEN = "EAAoP4cqGpxIBOxZBhbcy46uJyJ3UUuWbBiYUxz36taNXbcE9S054DwO2xSbcZCXUPdQyAHBxmR1vOH3aO1QW8NMVVK2YYGzCHX53Yx7WtNSg1GxVw8ZA3VEzOZATiHZBjnZA8NjZAM58MHuJfKP117gQ6QS8NCwcWeNaSrlXwrP9nZCV4ZABKzy3ZCTaZA7uz9XGgZDZD"
PHONE_NUMBER_ID = "696370466887605"

# Final uploaded media IDs
ITINERARY_MEDIA_IDS = {
    "pkg_bali": "1424268318490812",
    "pkg_ebc": "1480861172880220",
    "pkg_abc": "4082989858624005",
    "pkg_circuit": "1271909304532647"
}


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    elif request.method == "POST":
        # Incoming message
        data = request.get_json()
        print("🔔 Incoming:", json.dumps(data, indent=2))

        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    messages = value.get("messages")
                    if messages:
                        for msg in messages:
                            sender = msg["from"]

                            # If user tapped a button
                            if msg.get("type") == "interactive":
                                btn_id = msg["interactive"]["button_reply"]["id"]
                                if btn_id in ITINERARY_MEDIA_IDS:
                                    send_pdf(sender, ITINERARY_MEDIA_IDS[btn_id])
                                    return "OK", 200

                            # If user typed text
                            if msg.get("type") == "text":
                                text = msg["text"]["body"].strip().lower()
                                if "circuit" in text:
                                    send_pdf(sender, ITINERARY_MEDIA_IDS["pkg_circuit"])
                                else:
                                    send_package_buttons(sender)
                                    send_whatsapp_message(sender, "Looking for Annapurna Circuit? Just reply 'circuit' and I’ll send it!")
                                return "OK", 200
        return "OK", 200


def send_package_buttons(to):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "🙏 Thank you for reaching out!\nPlease choose a travel package:"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "pkg_bali", "title": "🏝️ Bali"}},
                    {"type": "reply", "reply": {"id": "pkg_ebc", "title": "🏔️ Everest BC"}},
                    {"type": "reply", "reply": {"id": "pkg_abc", "title": "🏔️ Annapurna BC"}}
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Sent buttons:", response.status_code, response.text)


def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Sent text:", response.status_code, response.text)


def send_pdf(to, media_id):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {
            "id": media_id,
            "caption": "📄 Here’s your itinerary!"
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Sent PDF:", response.status_code, response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)