# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a low-frequency quantitative trading learning project. The codebase implements a complete system from data acquisition to backtesting to strategy development.

## Architecture

The system follows a layered architecture:

```
data/          # Market data storage (SQLite)
backtest/      # Event-driven backtesting engine
strategies/    # Trading strategies (factor-based selection, timing)
reports/       # Backtest results and performance reports
```

Core philosophy: **self-built event-driven backtest framework** over third-party libraries — building from scratch produces the deepest understanding.

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data acquisition | yfinance (US stocks), akshare (A-share stocks) |
| Storage | SQLite |
| Analysis | pandas, numpy |
| Visualization | matplotlib, seaborn, plotly |
| Backtest | Custom event-driven (Week 3 of learning plan) |
| Production | vnpy (broker API integration) |

## Data Model

A-share stock data follows this naming convention:
- Stock code: `000001.SZ` (平安银行), `600000.SH` (浦发银行)
- K-line: OHLCV (Open/High/Low/Close/Volume)
- Financial data: PE, PB, ROE, revenue growth, cash flow

## Key Conventions

- All market data stored in SQLite with normalized schema
- Backtest engine uses event-driven model: signal generation → position management → performance calculation
- Each strategy module should be independently runnable and testable with the backtest engine
- Weekly deliverables must include: code + backtest report (returns, max drawdown, Sharpe ratio)

## Python Environment

Python 3.10+ with conda/venv. Core dependencies:
```
pandas numpy yfinance akshare matplotlib seaborn plotly sqlite3
```

## Development Workflow

1. Fetch and store data locally first (Week 1)
2. Build backtest engine (Week 3) — this is the core infrastructure
3. Implement strategies against the backtest engine
4. Validate with walk-forward analysis before trusting results
