# Oracle Project

## 🔮 What is this project?

Oracle Project is a public-facing Python toolkit for exploring market risk, trading signals, and option opportunity scanning.
It combines live market tools, historical scenario analysis, and a lightweight machine learning engine so traders and researchers can inspect market conditions with confidence.

## 🚀 Project Goals

- Help traders evaluate live exit and risk management decisions.
- Recreate historical market regimes and analyze how the same rules would have behaved.
- Train a predictive model on historical price behavior.
- Scan option markets for low-cost, high-opportunity setups.

## 📦 Repo structure

- `oracle_manager.py` — Live exit strategy assistant using Alpaca market quotes.
- `oracle_timemachine.py` — Historical context analyzer that loads a trained model and evaluates risk in past market conditions.
- `oracle_trainer.py` — Training script that builds a machine learning model from Alpaca historical data.
- `oracle_screener.py` — Live option scanner using Yahoo Finance to find budget-friendly trades.
- `oracle_brain.pkl` — Pre-trained model used by `oracle_timemachine.py`.
- `.env.example` — Template for environment variables.
- `.gitignore` — Protects local secrets and generated artifacts.
- `requirements.txt` — Python dependency list.

## 💡 Why this project matters

This repo is designed for transparency and reproducibility.
It keeps data access separate from code, uses public APIs for market data, and makes it easy for a newcomer to understand how the system is built.

## 🧠 Statistical and machine learning models used

- `RandomForestClassifier` from `scikit-learn`
  - Used in `oracle_trainer.py` to learn patterns from historical Alpaca data.
  - Produces a model saved as `oracle_brain.pkl`.
  - Used in `oracle_timemachine.py` to calculate probability estimates and validate historic scenarios.

## ⚙️ Requirements

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

If you run `oracle_screener.py`, install `yfinance` as well:

```bash
python -m pip install yfinance
```

## 🔧 Setup

1. Copy `.env.example` to `.env`.

```bash
copy .env.example .env
```

2. Add your Alpaca API credentials to `.env`:

```env
ALPACA_API_KEY=your_real_api_key
ALPACA_SECRET_KEY=your_real_secret_key
```

3. Keep `.env` local and do not commit it.

## ▶️ How to use each script

- `python oracle_manager.py`
  - Start live risk evaluation and exit signal assistance for a chosen ticker.

- `python oracle_timemachine.py`
  - Load historical market data and simulate how the model would have behaved in the past.

- `python oracle_trainer.py`
  - Train or retrain the `RandomForestClassifier` from historical data and save `oracle_brain.pkl`.

- `python oracle_screener.py`
  - Scan ticker lists using Yahoo Finance for option strategies that meet the repo's screening rules.

## 🧾 Notes for public use

- `oracle_manager.py`, `oracle_timemachine.py`, and `oracle_trainer.py` require Alpaca API credentials.
- `oracle_screener.py` uses Yahoo Finance only and does not need Alpaca credentials.
- This project is intended for research and educational use, not financial advice.

## ✅ Safe public publishing

The repo is safe to publish as long as you:

1. Never commit a real `.env` file.
2. Keep AWS/Alpaca credentials private.
3. Use `.env.example` for placeholder values only.

`.gitignore` already excludes `.env`, `*.env`, logs, and compiled Python files.

## 📣 Summary

Oracle Project is a clean, public-ready trading utility collection that bridges live scanning, historical analysis, and machine learning.
It highlights a `RandomForestClassifier` model trained on market history and provides a usable setup for broader experimentation.

