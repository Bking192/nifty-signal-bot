
import time
import requests
from datetime import datetime
import re

# === CONFIG ===
TOKEN = '7854126953:AAFhXGIp-ISlVEcFDpTJ2XzaAeQCmzHg49o'
CHAT_ID = '633573219'
INTERVAL = 300  # 5 minutes

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

def send_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        res = requests.post(url, data=payload)
        print("Sent:", res.status_code)
    except Exception as e:
        print("Failed to send alert:", e)

def fetch_nifty_spot():
    try:
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        session = requests.Session()
        session.get('https://www.nseindia.com', headers=HEADERS)
        response = session.get(url, headers=HEADERS)
        data = response.json()
        return float(data['records']['underlyingValue'])
    except Exception as e:
        print("Error fetching spot price:", e)
        return None

def get_atm_strike(spot):
    return int(round(spot / 100.0) * 100)

def get_option_price(spot, option_type='CE'):
    try:
        atm_strike = get_atm_strike(spot)
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        session = requests.Session()
        session.get('https://www.nseindia.com', headers=HEADERS)
        response = session.get(url, headers=HEADERS)
        data = response.json()
        for d in data['records']['data']:
            if d['strikePrice'] == atm_strike:
                return d['CE' if option_type == 'CE' else 'PE']['lastPrice'], atm_strike
    except Exception as e:
        print("Error fetching option price:", e)
    return None, None

def check_signals():
    spot = fetch_nifty_spot()
    if not spot:
        return

    # Simulate indicator values
    import numpy as np
    rsi = np.random.randint(35, 65)
    adx = np.random.randint(15, 30)
    close = spot
    high_10 = spot + 50
    low_10 = spot - 50

    if rsi > 45 and adx > 20 and close > high_10:
        price, strike = get_option_price(spot, 'CE')
        if price:
            target = round(price * 1.05, 2)
            sl = round(price * 0.975, 2)
            send_alert(f"📈 BUY NIFTY {strike} CE @ ₹{price}\n🎯 Target: ₹{target} | ❌ SL: ₹{sl}")

    elif rsi < 55 and adx > 20 and close < low_10:
        price, strike = get_option_price(spot, 'PE')
        if price:
            target = round(price * 1.05, 2)
            sl = round(price * 0.975, 2)
            send_alert(f"📉 BUY NIFTY {strike} PE @ ₹{price}\n🎯 Target: ₹{target} | ❌ SL: ₹{sl}")

# === MAIN LOOP ===
while True:
    check_signals()
    time.sleep(INTERVAL)
