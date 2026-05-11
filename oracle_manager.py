import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

# Load Secrets
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

print(r"""
===================================================
   🛑 ORACLE MANAGER (EXIT STRATEGY)
   [Status: ONLINE]
===================================================
""")

# 1. Ask User for Trade Details
ticker = input("🎫 Which Ticker are you holding? (e.g., NIO): ").upper()
entry_price = float(input(f"💰 What price did you pay per contract? (e.g., 0.24): "))
days_held = int(input("📅 How many days have you held it? (0 for today): "))

# 2. Get Live Data
print(f"\n🔍 Checking live status for {ticker}...")

try:
    # Get the Stock Price
    trade = api.get_latest_trade(ticker)
    current_stock_price = float(trade.price)
    
    # Simple "Greeks" Estimation (Rule of Thumb for Beginners)
    # If stock is UP, Option is UP.
    print(f"📈 Stock Price Now: ${current_stock_price:.2f}")

    # 3. Decision Logic
    # OPTION ESTIMATOR (Very rough math for "At The Money" options)
    # A $0.50 move in stock approx = $0.25 move in option (Delta 0.5)
    
    print("-" * 40)
    print("🤖 ORACLE ADVICE:")
    
    # EXIT RULE 1: TIME DECAY
    if days_held > 10:
        print(f"⚠️ SELL NOW (Time Decay Risk). You have held too long.")
        print("   Options lose value every day. Take whatever cash is left.")
        
    # EXIT RULE 2: PROFIT TARGET (+25%)
    # We can't see the exact option price here, so we give you the rules.
    else:
        target_sell = entry_price * 1.25  # +25%
        stop_loss = entry_price * 0.70    # -30%
        
        print(f"🎯 PROFIT TARGET: Sell if Option Price hits ${target_sell:.2f}")
        print(f"🛑 STOP LOSS:     Sell if Option Price drops to ${stop_loss:.2f}")
        print("-" * 40)
        print("👀 CHECK ROBINHOOD NOW:")
        print(f"   - Is the current Option Price > ${target_sell:.2f}? -> SELL (Take Profit)")
        print(f"   - Is the current Option Price < ${stop_loss:.2f}? -> SELL (Cut Loss)")
        print(f"   - Is it in between? -> HOLD (Let it ride)")

except Exception as e:
    print(f"Error: {e}")