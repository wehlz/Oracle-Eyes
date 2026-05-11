# Project: ORACLE (Evolution of Olympus Eyes) - Training Module
# ============================================================

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
import joblib
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load Secrets
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

# Check for keys
if not API_KEY or not SECRET_KEY:
    print("❌ ERROR: Keys not found in .env file.")
    exit()

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# --- CONFIGURATION ---
TICKERS = ["SPY", "QQQ", "IWM", "NVDA", "TSLA", "AMD", "AAPL", "MSFT", "GOOGL", "AMZN", "SOFI", "PLTR", "HOOD", "F", "GM"]
print(f"[ORACLE] System initializing... Downloading data for {len(TICKERS)} assets.")

def calculate_features(df):
    """
    Engineers the 'Alpha' features. 
    Using robust manual Pandas math to ensure stability.
    """
    df = df.copy()
    
    # 1. Daily Returns (Pct_Change)
    df['Pct_Change'] = df['close'].pct_change()
    
    # 2. RSI (14-day) - Momentum
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # 3. ATR Normalized (Volatility)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(14).mean()
    df['ATR_Norm'] = atr / df['close'] 
    
    # 4. Relative Volume (Institutional Interest)
    df['Rel_Vol'] = df['volume'] / df['volume'].rolling(20).mean()
    
    return df

def prepare_data():
    all_data = []
    
    # FIX: Explicitly format start date as YYYY-MM-DD string to satisfy Alpaca API
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    for ticker in TICKERS:
        try:
            print(f"Downloading {ticker}...")
            # Fetch 2 years of data using the clean start_date string
            bars = api.get_bars(ticker, "1Day", start=start_date, limit=None).df
            
            if bars.empty:
                print(f"   Warning: No data returned for {ticker}")
                continue
                
            # Calculate Features
            bars = calculate_features(bars)
            
            # --- THE TARGET ---
            # Did the price close HIGHER tomorrow? (1 = Yes, 0 = No)
            bars["Target"] = (bars["close"].shift(-1) > bars["close"]).astype(int)
            
            bars = bars.dropna()
            all_data.append(bars)
            print(f"   Ingested {len(bars)} days")
            
        except Exception as e:
            print(f"   Error with {ticker}: {e}")
            
    if not all_data:
        print("CRITICAL: No data collected. Check internet or API keys.")
        exit()
        
    return pd.concat(all_data)

# --- EXECUTION ---
data = prepare_data()

# Features used for prediction
predictors = ["RSI_14", "ATR_Norm", "Rel_Vol", "Pct_Change"]

# Split Data (Train on Past, Test on Recent)
train_size = int(len(data) * 0.8)
train = data.iloc[:train_size]
test = data.iloc[train_size:]

# Initialize the Random Forest (The Brain)
model = RandomForestClassifier(n_estimators=200, min_samples_leaf=25, random_state=42)

print("\n[ORACLE] Training Neural Pathways (Random Forest)...")
model.fit(train[predictors], train["Target"])

# Verify Accuracy
preds = model.predict(test[predictors])
precision = precision_score(test["Target"], preds)

print("="*40)
print(f"MODEL PRECISION: {precision:.2%}")
print("="*40)

if precision > 0.53:
    print("STATUS: PASS. Model has an edge.")
    joblib.dump(model, "oracle_brain.pkl")
    print("Brain saved to 'oracle_brain.pkl'")
else:
    print("STATUS: WEAK. Consider adding more data.")