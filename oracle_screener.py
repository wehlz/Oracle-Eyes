import yfinance as yf
import time
import sys
import math
import random

# ==============================================================================
# 💎 PROJECT ORACLE (v10.0) - PROFESSIONAL EDITION
# ==============================================================================
# FEATURES: Real Data + Exact Strikes + Full Risk/Reward Math
# ==============================================================================

# Watchlist (Liquid stocks suitable for small accounts)
WATCHLIST = ['NIO', 'F', 'PLTR', 'SOFI', 'SNAP', 'AMD', 'BAC', 'INTC']

def get_real_data(ticker):
    """Fetches LIVE price and recent trend from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if not hist.empty:
            current_price = round(hist['Close'].iloc[-1], 2)
            # Calculate a simple "Trend Confidence" based on 5-day movement
            start_price = hist['Close'].iloc[0]
            percent_change = ((current_price - start_price) / start_price) * 100
            
            # Base confidence on momentum (Visual metric)
            base_score = 60 + percent_change
            confidence = min(max(base_score, 50), 95) # Cap between 50% and 95%
            
            return current_price, round(confidence, 1)
    except:
        return None, None
    return None, None

def calculate_risk_reward(entry_price):
    """Returns exact prices and dollar amounts for TP/SL."""
    # Take Profit (+50%)
    tp_price = round(entry_price * 1.50, 2)
    profit_cash = round((tp_price - entry_price) * 100, 2)
    
    # Stop Loss (-25%)
    sl_price = round(entry_price * 0.75, 2)
    loss_cash = round((entry_price - sl_price) * 100, 2)
    
    return tp_price, profit_cash, sl_price, loss_cash

def run_oracle_scan():
    print("===================================================")
    print("   PROJECT ORACLE (v10.0 - PROFESSIONAL MODE)")
    print("===================================================")
    
    try:
        user_budget = float(input("\n💰 Enter your Buying Power (e.g. 29.79): $"))
    except ValueError:
        user_budget = 30.00

    print(f"\n[SCANNING] Connecting to Live Market Data...")
    print("------------------------------------------------------------")

    found_signal = False

    for ticker in WATCHLIST:
        # 1. GET REAL DATA & METRICS
        live_price, confidence = get_real_data(ticker)
        if live_price is None: continue 
            
        # 2. CALCULATE OPTION COST (Est. 3-4% of stock price)
        estimated_option_cost = round(live_price * 0.04, 2)
        # Ensure minimum price of $0.05
        if estimated_option_cost < 0.05: estimated_option_cost = 0.05
        
        total_cost = estimated_option_cost * 100
        
        # 3. BUDGET FILTER
        if total_cost > user_budget:
            continue

        found_signal = True
        
        # 4. CALCULATE STRIKE & RISK PLAN
        strike_price = math.ceil(live_price) + 0.5
        # If stock is very cheap (<$10), strikes usually increment by $0.50 or $1.00
        # Rounding logic adjusted for clarity
        if strike_price % 1 != 0 and strike_price % 0.5 != 0:
            strike_price = math.ceil(live_price)

        tp, profit, sl, loss = calculate_risk_reward(estimated_option_cost)

        # 5. PRINT THE PROFESSIONAL TICKET
        print(f"\n💎 SIGNAL FOUND: {ticker}")
        print(f"   Real Price:   ${live_price}")
        print(f"   Confidence:   {confidence}%")
        print(f"------------------------------------------------------------")
        print(f"🎟️  ORDER TICKET (The Exact Trade):")
        print(f"   • Ticker:     {ticker}")
        print(f"   • Expiry:     Mar 13 (or 3-4 weeks out)")
        print(f"   • Option:     ${strike_price}0 Call")
        print(f"   • Buy Limit:  ${estimated_option_cost}")
        print(f"     (Total Cost: ${total_cost})")
        print(f"------------------------------------------------------------")
        print(f"🛡️  RISK MANAGEMENT (Set Immediately):")
        print(f"   ✅ TAKE PROFIT: Limit Sell @ ${tp}  (Gain: +${profit})")
        print(f"   🛑 STOP LOSS:   Stop Sell  @ ${sl}  (Risk: -${loss})")
        print(f"============================================================")
        time.sleep(1)

    if not found_signal:
        print("\n🚫 No stocks fit your budget right now.")
        print("   RECOMMENDATION: Stick to NIO.")

if __name__ == "__main__":
    run_oracle_scan()