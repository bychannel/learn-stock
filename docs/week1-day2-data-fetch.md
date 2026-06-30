# 第 1 周 · 第 2 天：行情数据获取

> 目标：掌握 akshare 获取 A 股历史K线和实时行情的方法

---

## 1. 今日任务清单

- [ ] 获取单只股票历史日K线数据
- [ ] 获取多只股票历史数据
- [ ] 获取实时行情数据
- [ ] 将数据保存到 SQLite
- [ ] 验证数据完整性

---

## 2. 历史 K 线数据获取

在 Jupyter Notebook 中执行以下代码：

### 2.1 单只股票历史日K线

```python
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 获取平安银行（000001.SZ）近一年日K线
df = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20250630",
    end_date="20260630"
)

print(f"数据形状: {df.shape}")
print(f"列名: {list(df.columns)}")
print(df.head())
print("\n数据时间范围:", df['日期'].min(), "至", df['日期'].max())
```

### 2.2 批量获取多只股票

```python
# 定义股票池（金融板块+消费板块示例）
stock_list = [
    "000001.SZ",  # 平安银行
    "600000.SH",  # 浦发银行
    "600519.SH",  # 贵州茅台
    "000858.SZ",  # 五粮液
    "600036.SH",  # 招商银行
]

# 获取所有股票近一年数据
all_data = {}
for code in stock_list:
    symbol = code.replace(".SZ", "").replace(".SH", "")
    market = "sz" if code.endswith(".SZ") else "sh"

    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date="20250630",
        end_date="20260630"
    )
    all_data[code] = df
    print(f"✅ {code} 获取成功: {len(df)} 条记录")

print(f"\n共获取 {len(all_data)} 只股票数据")
```

---

## 3. 实时行情数据获取

```python
# 获取实时行情（涨跌幅、成交量、市值等）
df_realtime = ak.stock_zh_a_spot_em()

print(f"实时行情数据形状: {df_realtime.shape}")
print(f"列名: {list(df_realtime.columns)[:15]}")  # 只显示前15列
print(df_realtime.head())

# 筛选特定股票
target_stocks = ["平安银行", "贵州茅台", "招商银行"]
df_filtered = df_realtime[df_realtime['名称'].isin(target_stocks)]
print("\n目标股票实时行情:")
print(df_filtered[['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额']])
```

---

## 4. 数据保存到 SQLite

```python
import sqlite3
import os

# 创建数据目录（如果不存在）
os.makedirs("data", exist_ok=True)

# 连接 SQLite 数据库
conn = sqlite3.connect("data/stock_data.db")
cursor = conn.cursor()

# 创建日K线表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_code TEXT NOT NULL,
        date DATE NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        amount REAL,
        PRIMARY KEY (stock_code, date)
    )
""")

# 插入数据（替换模式：若已存在则更新）
for code, df in all_data.items():
    # 重命名列以匹配数据库结构
    df_renamed = df.rename(columns={
        '日期': 'date',
        '开盘': 'open',
        '最高': 'high',
        '最低': 'low',
        '收盘': 'close',
        '成交量': 'volume',
        '成交额': 'amount'
    })
    df_renamed['stock_code'] = code

    # 替换数据
    df_renamed.to_sql('stock_daily', conn, if_exists='replace', index=False)
    print(f"📦 {code} 数据已保存")

conn.close()
print("\n✅ 数据库保存完成: data/stock_data.db")
```

---

## 5. 数据验证

```python
# 验证数据库内容
conn = sqlite3.connect("data/stock_data.db")

# 检查表数量
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("数据库表:", cursor.fetchall())

# 检查各股票记录数
cursor.execute("""
    SELECT stock_code, COUNT(*) as count, MIN(date), MAX(date)
    FROM stock_daily
    GROUP BY stock_code
""")
print("\n各股票数据统计:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} 条 ({row[2]} ~ {row[3]})")

conn.close()
```

---

## 6. 完整脚本

将以上代码整合为一个可复用的数据获取脚本，保存到 `data/fetch_data.py`：

```python
"""
data/fetch_data.py
==================
A股历史K线数据获取脚本
"""
import akshare as ak
import pandas as pd
import sqlite3
import os
from datetime import datetime

def fetch_stock_daily(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取单只股票历史日K线"""
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
    return df

def save_to_sqlite(data_dict: dict, db_path: str = "data/stock_data.db"):
    """保存股票数据到SQLite"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)

    for code, df in data_dict.items():
        df_copy = df.copy()
        df_copy['stock_code'] = code
        df_copy.to_sql('stock_daily', conn, if_exists='replace', index=False)
        print(f"📦 {code} 已保存: {len(df)} 条")

    conn.close()
    print(f"✅ 保存完成: {db_path}")

if __name__ == "__main__":
    # 示例：获取金融板块股票
    stocks = {
        "000001.SZ": "平安银行",
        "600000.SH": "浦发银行",
        "600036.SH": "招商银行",
    }

    all_data = {}
    for code in stocks.keys():
        symbol = code.replace(".SZ", "").replace(".SH", "")
        df = fetch_stock_daily(symbol, "20250630", "20260630")
        all_data[code] = df

    save_to_sqlite(all_data)
```

---

## 7. 今日成果

完成今天的学习后，你将：
1. 掌握使用 akshare 获取 A 股历史K线和实时行情
2. 学会将数据存储到 SQLite 数据库
3. 拥有可复用的数据获取脚本
4. 为明天的数据存储方案设计做好准备

---

## 常见问题

**Q: 获取数据报错 "请求过于频繁"**
> akshare 有频率限制，在循环中添加延时：
> `import time; time.sleep(1)`

**Q: 某些股票没有数据**
> 检查股票代码是否正确，或尝试获取更短的时间范围

**Q: SQLite 数据库打不开**
> 使用 SQLiteViewer 插件或 DBeaver 工具查看数据库内容
