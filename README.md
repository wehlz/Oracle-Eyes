# Oracle Project

A small Python toolkit for trading signal generation, historical scenario analysis, and option risk planning.

## What this repo contains

- `oracle_manager.py` — Live exit-strategy assistant using Alpaca quotes.
- `oracle_timemachine.py` — Historical market context analyzer with regime-aware backtest logic.
- `oracle_trainer.py` — Training module that builds a RandomForest model from Alpaca historical data.
- `oracle_screener.py` — Live scanning utility using Yahoo Finance to identify budget-friendly option setups.
- `oracle_brain.pkl` — Pre-trained model used by `oracle_timemachine.py`.
- `.env.example` — Placeholder environment variables for Alpaca credentials.
- `.gitignore` — Prevents committing local secrets and generated files.
- `requirements.txt` — Python dependencies.

## Safe GitHub publishing

Yes — this repo is safe to publish publicly as long as you:

1. Do not commit a real `.env` file.
2. Keep the `.env` file local to your machine.
3. Use `.env.example` only for placeholder values.

`.gitignore` is included and already ignores `.env`, `*.env`, logs, compiled Python files, and other local artifacts.

## Requirements

Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

If you run `oracle_screener.py`, you will also need `yfinance`:

```bash
python -m pip install yfinance
```

## Setup

1. Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

2. Fill in your Alpaca keys in `.env`:

```env
ALPACA_API_KEY=your_real_api_key
ALPACA_SECRET_KEY=your_real_secret_key
```

3. Do not commit `.env`.

## Usage

- `python oracle_manager.py` — Evaluate live exit criteria for a ticker.
- `python oracle_timemachine.py` — Reconstruct a historical market scenario and check risk settings.
- `python oracle_trainer.py` — Train or retrain the market prediction model.
- `python oracle_screener.py` — Scan a watchlist for budget-friendly options signals.

## Notes

- `oracle_trainer.py`, `oracle_manager.py`, and `oracle_timemachine.py` rely on Alpaca API credentials.
- `oracle_screener.py` uses Yahoo Finance and does not require Alpaca credentials.
- Keep your real credentials out of source control by using `.env` locally.
