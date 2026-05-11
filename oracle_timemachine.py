import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import joblib
import os
import requests
import math
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load Secrets
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# --- CONFIGURATION ---
COMPANY_MAP = {
    "PLTR": "Palantir stock", "SOFI": "SoFi stock", "HOOD": "Robinhood stock",
    "UBER": "Uber stock", "SNAP": "Snap Inc stock", "DKNG": "DraftKings stock",
    "RIOT": "Riot Platforms stock", "MARA": "Marathon Digital stock"
}
WATCHLIST = [
    "PLTR", "SOFI", "HOOD", "UBER", "SNAP", "DKNG", "INTC", "COIN", "MARA", "RIOT",
    "NU", "F", "GM", "TSLA", "CCL", "AAL", "HAL", "OPEN", "NIO", "LCID"
]
predictors = ["RSI_14", "ATR_Norm", "Rel_Vol", "Pct_Change"]

print(r"""
===================================================
   🔮 ORACLE TIME MACHINE (v3.0 - REGIME AWARE)
   [Capability: Historical Trend Protection]
   [Status: ONLINE]
===================================================
""")

# 1. Load Brain
if not os.path.exists("oracle_brain.pkl"):
    print("❌ Brain missing.")
    exit()
model = joblib.load("oracle_brain.pkl")

# 2. User Inputs
date_str = input("📅 Enter Historical Date (YYYY-MM-DD): ")
try:
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
except ValueError:
    print("❌ Invalid format.")
    exit()

budget_str = input("💰 Enter Historical Budget (e.g., 1000): $")
try:
    MAX_BUDGET = float(budget_str)
except:
    MAX_BUDGET = 1000.0

print(f"\n⏳ Reconstructing Market Context for {date_str}...\n")

# --- HISTORICAL SAFETY CHECK ---
def check_historical_market_health(date_obj):
    """Travels back to see if SPY was healthy ON THAT DAY."""
    try:
        # We need 300 days PRIOR to the target date to calculate the 200MA
        end_fetch = date_obj.strftime("%Y-%m-%d")
        start_fetch = (date_obj - timedelta(days=400)).strftime("%Y-%m-%d")
        
        spy_bars = api.get_bars("SPY", "1Day", start=start_fetch, end=end_fetch).df
        
        if spy_bars.empty: return "BEAR" # Safe default
        
        # Get the price on the TARGET DATE
        spy_on_date = spy_bars.iloc[-1]
        close_price = spy_on_date['close']
        
        # Calculate 200MA
        ma_200 = spy_bars['close'].rolling(200).mean().iloc[-1]
        
        if pd.isna(ma_200): return "BULL" # Not enough data, assume bull
        
        dist = ((close_price - ma_200) / ma_200) * 100
        
        if close_price < ma_200:
            print(f"⚠️ HISTORICAL ALERT: On this date, SPY was {dist:.2f}% BELOW trend.")
            print("   (Market was in a Crash/Correction -> Enabling Strict Filters)")
            return "BEAR"
        else:
            print(f"✅ HISTORICAL CLEAR: On this date, SPY was {dist:.2f}% ABOVE trend.")
            return "BULL"
            
    except Exception as e:
        print(f"⚠️ Error checking SPY: {e}")
        return "BEAR"

# Check the Regime
market_status = check_historical_market_health(target_date)
CONFIDENCE_THRESHOLD = 0.65 if market_status == "BEAR" else 0.55

print(f"[BACKTEST] Threshold adjusted to {CONFIDENCE_THRESHOLD*100}%...\n")


# --- FUNCTIONS ---
def get_past_news(ticker, date_obj):
    headlines = []
    end_str = date_obj.strftime("%Y-%m-%d")
    start_str = (date_obj - timedelta(days=5)).strftime("%Y-%m-%d")
    search_term = COMPANY_MAP.get(ticker, f"{ticker} stock")
    try:
        query = f"{search_term} news after:{start_str} before:{end_str}"
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            for i, item in enumerate(items):
                if i >= 3: break
                title = item.find('title').text
                headlines.append(f"[Google] {title}")
    except: pass
    return headlines if headlines else ["No specific news found."]

def calculate_features(df):
    df = df.copy()
    df['Pct_Change'] = df['close'].pct_change()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(14).mean()
    df['ATR_Norm'] = atr / df['close'] 
    df['Rel_Vol'] = df['volume'] / df['volume'].rolling(20).mean()
    return df

# --- SIMULATION ---
hits = 0

for ticker in WATCHLIST:
    try:
        # 1. Fetch History
        end_fetch = (target_date + timedelta(days=5)).strftime("%Y-%m-%d")
        bars = api.get_bars(ticker, "1Day", start=(target_date - timedelta(days=300)).strftime("%Y-%m-%d"), end=end_fetch).df
        
        if bars.empty: continue
        
        # 2. Isolate "The Past"
        past_view = bars[bars.index.strftime('%Y-%m-%d') <= date_str]
        if past_view.empty: continue
        current_price = past_view.iloc[-1]['close']
        
        if current_price > MAX_BUDGET: continue

        # 3. Math
        past_view = calculate_features(past_view)
        today_features = past_view.iloc[-1:][predictors]
        if today_features.isnull().values.any(): continue
        
        # 4. Brain Decision
        prob_up = model.predict_proba(today_features)[0][1]
        
        # ⛔ DYNAMIC FILTER APPLIED HERE
        if prob_up <= CONFIDENCE_THRESHOLD: continue

        # 5. Future Check
        future_view = bars[bars.index.strftime('%Y-%m-%d') > date_str]
        if future_view.empty:
            result = "UNKNOWN"
        else:
            next_close = future_view.iloc[0]['close']
            pct_move = ((next_close - current_price) / current_price) * 100
            if next_close > current_price:
                result = f"✅ WIN (+{pct_move:.2f}%)"
            else:
                result = f"❌ LOSS ({pct_move:.2f}%)"

        # 6. Report
        shares = math.floor(MAX_BUDGET / current_price)
        cost = shares * current_price
        headlines = get_past_news(ticker, target_date)

        print("-" * 65)
        print(f"👁️  SIGNAL FOUND: {ticker}")
        print(f"💰  Buy {shares} shares @ ${current_price:.2f} (Cost: ${cost:.2f})")
        print(f"🧠  Confidence: {prob_up*100:.1f}%")
        print(f"🔮  RESULT (Next Day): {result}")
        print(f"\n📰  News Context:")
        for h in headlines:
            print(f"    - {h}")
        print("-" * 65)
        hits += 1

    except Exception as e:
        pass

if hits == 0:
    print(f"🚫 No signals found above {CONFIDENCE_THRESHOLD*100}% confidence.")
    if market_status == "BEAR":
        print("   (The Oracle correctly avoided trading during this Market Crash.)")