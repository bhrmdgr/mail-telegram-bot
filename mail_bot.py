import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import requests
import re
from email.utils import parseaddr
from bs4 import BeautifulSoup

# Telegram bot bilgileri
TOKEN = "8154288966:AAFZw5KfD5zCqX4KmLiNqBIyTdUd4laOuFg"
CHAT_ID = "1086435098"

# Markdown karakterlerinden kaç
def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

# Mail içeriğini sadeleştir
def temizle_mail_icerigi(text):
    text = re.sub(r'[ \t]+', ' ', text)  # Fazla boşlukları sil
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Çoklu boş satırları azalt
    return text.strip()

# Telegram'a gönder
def send_to_telegram(subject, sender, date, body):
    subject = escape_markdown(subject)
    sender = escape_markdown(sender)
    date = escape_markdown(date)
    body = escape_markdown(body)

    message = f"📩 *Yeni Mail*\n\n*Başlıkk:* {subject}\n*Gönderenn:* {sender}\n*Tarih:* {date}\n\n*İçerikk:*\n{body}"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message[:4096],
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)

# Gmail IMAP sunucusu bilgileri
imap_server = "imap.gmail.com"
mail = imaplib.IMAP4_SSL(imap_server)

# Giriş
username = "bhrmdgr@gmail.com"
password = "lwgs busi myfh pziz"

try:
    mail.login(username, password)
    print("Giriş başarılı!")
except Exception as e:
    print(f"Bir hata oluştu: {e}")

mail.select("inbox")

# Son 4 saat içindeki mailleri kontrol et
now = datetime.now()
since_time = now - timedelta(hours=4)
since_str = since_time.strftime("%d-%b-%Y")

print(f"Son 4 saatlik zaman dilimi: {since_str} - Şu anki zaman: {now.strftime('%d-%b-%Y %H:%M:%S')}")

status, messages = mail.search(None, f"SINCE {since_str}")
message_ids = messages[0].split()

for msg_id in message_ids:
    status, msg_data = mail.fetch(msg_id, "(RFC822)")

    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            date_str = msg["Date"]
            date_tuple = email.utils.parsedate_tz(date_str)
            if date_tuple:
                msg_time = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                if since_time <= msg_time <= now:
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    sender = parseaddr(msg.get("From"))[1]
                    date = msg_time.strftime('%d-%b-%Y %H:%M:%S')

                    # Mail içeriği çözümleme
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if "attachment" not in content_disposition:
                                payload = part.get_payload(decode=True)
                                charset = part.get_content_charset()
                                try:
                                    decoded = payload.decode(charset or 'utf-8', errors='ignore')
                                    if content_type == "text/plain":
                                        body = temizle_mail_icerigi(decoded)
                                        break
                                    elif content_type == "text/html":
                                        soup = BeautifulSoup(decoded, "html.parser")
                                        text = soup.get_text(separator="\n")
                                        body = temizle_mail_icerigi(text)
                                except:
                                    continue
                        if not body:
                            body = "(Mail içeriği boş görünüyor)"
                    else:
                        payload = msg.get_payload(decode=True)
                        charset = msg.get_content_charset()
                        try:
                            decoded = payload.decode(charset or 'utf-8', errors='ignore')
                            if msg.get_content_type() == "text/html":
                                soup = BeautifulSoup(decoded, "html.parser")
                                text = soup.get_text(separator="\n")
                                body = temizle_mail_icerigi(text)
                            else:
                                body = temizle_mail_icerigi(decoded)
                        except Exception as e:
                            body = "(İçerik çözümlenemedi)"

                    # İçeriği sınırlama
                    if len(body) > 3500:
                        body = body[:3500] + "\n\n...(İçerik kısaltıldı)"

                    print(f"Başlık: {subject}")
                    print(f"Gönderen: {sender}")
                    print(f"Tarih: {date}")
                    print("Mail İçeriği (Temizlenmiş):")
                    print(body)

                    # Telegram'a gönder
                    send_to_telegram(subject, sender, date, body)
                    print("✔ Telegram'a mesaj gönderildi.")
