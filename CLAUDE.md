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
| Data acquisition | akshare (A-share stocks only) |
| Storage | MySQL |
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

Python 3.10+ with **uv** (faster, lighter than Anaconda). Core dependencies:
```
pandas numpy akshare matplotlib seaborn plotly sqlite3
```

### 环境初始化（Linux 服务器）

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv quant_env --python 3.11
source quant_env/bin/activate

# 安装依赖
uv pip install pandas numpy matplotlib seaborn plotly akshare jupyter
```

### 环境初始化（Windows 本地）

```powershell
# 安装 uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 创建虚拟环境
uv venv quant_env --python 3.11
quant_env\Scripts\activate

# 安装依赖
uv pip install pandas numpy matplotlib seaborn plotly akshare jupyter
```

## Development Workflow

1. Fetch and store data locally first (Week 1)
2. Build backtest engine (Week 3) — this is the core infrastructure
3. Implement strategies against the backtest engine
4. Validate with walk-forward analysis before trusting results
