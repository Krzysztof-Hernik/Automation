import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv()

now = datetime.now(ZoneInfo("Europe/Vienna"))

print(f"Aktualny czas: {now}")

if now.hour != 8 or now.minute > 55:
    print("Poza oknem czasowym – kończę")
    exit(0)

# if now.hour != 10:
#     print("To nie 10:00")
#     sys.exit(0)

# if now.minute > 5:
#     print("Za późno")
#     sys.exit(0)

# if not ("10:00" <= now <= "10:20"):
#     print("Poza oknem czasowym – exit")
#     sys.exit(0)

if os.path.exists("ran.txt"):
    print("Już wykonane dziś")
    sys.exit(0)

# ===== TWOJA LOGIKA =====
# fetch kurs
# send email
# send discord
# =======================

with open("ran.txt", "w") as f:
    f.write(str(datetime.now()))

# ————————— CONFIG —————————

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 587))
EMAIL_FROM  = os.getenv("EMAIL_FROM")
EMAIL_TO    = os.getenv("EMAIL_TO")
EMAIL_PASS  = os.getenv("EMAIL_PASS")

# ————————— FETCH RATE —————————


def get_usd_pln():
    try:
        url = "https://api.nbp.pl/api/exchangerates/rates/A/USD/?format=json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data["rates"][0]["mid"]
    except Exception as e:
        print("Błąd API:", e)
        return None

# ————————— SEND EMAIL —————————


def send_email(rate):
    subject = f"Kurs USD/PLN — {datetime.now().strftime('%Y-%m-%d')}"
    body = f"""
    Dzień dobry,

    aktualny średni kurs USD / PLN (NBP):

    💵 1 USD = {rate:.4f} PLN

    Data: {datetime.now().strftime('%Y-%m-%d')}
    Źródło: Narodowy Bank Polski
    
    Twój boteł
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"]   = EMAIL_TO
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    print("EMAIL_PASS:", "OK" if os.getenv("EMAIL_PASS") else "BRAK")
    print("EMAIL_FROM:", os.getenv("EMAIL_FROM"))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_FROM, EMAIL_PASS)
            smtp.send_message(msg)
        print("Email wysłany ✔")
    except Exception as e:
        print("Błąd wysyłania emaila:", e)

# ————————— SEND DISCORD —————————


def send_discord(rate):
    webhook = os.getenv("DISCORD_WEBHOOK")
    if not webhook:
        return

    message = {
        "content": (
            f"📊 **USD / PLN (NBP)**\n"
            f"💵 1 USD = **{rate:.4f} PLN**\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d')}"
        )
    }

    try:
        requests.post(webhook, json=message, timeout=10)
    except Exception as e:
        print("Błąd Discord:", e)

# ————————— MAIN —————————


def main():
    rate = get_usd_pln()
    if rate is not None:
        send_email(rate)
        send_discord(rate)
    else:
        print("Nie udało się pobrać kursu.")


if __name__ == "__main__":
    main()
