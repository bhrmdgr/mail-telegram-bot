import requests

TOKEN = "8154288966:AAFZw5KfD5zCqX4KmLiNqBIyTdUd4laOuFg"
CHAT_ID = "1086435098"

def test_telegram():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🔔 Test mesajı kraldan geliyor!"
    }
    response = requests.post(url, data=payload)
    print(f"Telegram yanıtı: {response.status_code} - {response.text}")

test_telegram()
