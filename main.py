import os
import time
import requests
import pandas as pd
import ta
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_signal(pair, action, rsi_val):
    message = (
        f"📊 **Quotex High-Probability Signal**\n\n"
        f"💱 **Pair:** {pair}\n"
        f"⏰ **Timeframe:** 1 MIN\n"
        f"⌛ **Expiration:** 1-3 MIN\n"
        f"📈 **Action:** {action} {'🟢' if 'BUY' in action else '🔴'}\n"
        f"📉 **RSI Value:** {round(rsi_val, 2)}\n\n"
        f"⚠️ *دڵنیابەوە لە بەڕێوەبردنی سەرمایەکەت!*"
    )
    bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode="Markdown")

def analyze_market():
    url = "https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=60"
    response = requests.get(url).json()
    
    df = pd.DataFrame(response, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    df = df.iloc[::-1].reset_index(drop=True)
    
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
    
    last = df.iloc[-1]
    rsi = last['rsi']
    close = last['close']
    ema = last['ema50']
    
    # مەرجەکانی سیگناڵی بەهێز
    if rsi < 30 and close > ema:
        send_signal("BTC/USD", "CALL (BUY)", rsi)
    elif rsi > 70 and close < ema:
        send_signal("BTC/USD", "PUT (SELL)", rsi)

if __name__ == "__main__":
    print("بۆتەکە چالاک کرا...")
    while True:
        try:
            analyze_market()
        except Exception as e:
            print(f"هەڵە: {e}")
        time.sleep(60)
