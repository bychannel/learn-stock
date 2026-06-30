# 第 1 周 · 第 2 天：行情数据获取

> 目标：掌握 akshare 获取 A 股历史K线和实时行情的方法

---

## 1. 今日任务清单

- [x] 获取单只股票历史日K线数据
- [x] 获取多只股票历史数据
- [x] 获取实时行情数据
- [x] 将数据保存到 MySQL
- [x] 验证数据完整性

---

## ✅ 完成任务

> 完成日期：2026-06-30

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

## 4. 数据保存到 MySQL

### 4.1 安装 MySQL 连接器

```bash
uv pip install pymysql sqlalchemy
```

### 4.2 创建数据库和表

```python
import pymysql

# 连接 MySQL（根据你的配置修改 host/user/password）
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='quant_db',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 创建数据库（如果不存在）
cursor.execute("CREATE DATABASE IF NOT EXISTS quant_db CHARACTER SET utf8mb4")
cursor.execute("USE quant_db")

# 创建日K线表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_daily (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stock_code VARCHAR(20) NOT NULL,
        trade_date DATE NOT NULL,
        open DECIMAL(10, 2),
        high DECIMAL(10, 2),
        low DECIMAL(10, 2),
        close DECIMAL(10, 2),
        volume DECIMAL(20, 2),
        amount DECIMAL(20, 2),
        UNIQUE KEY uk_code_date (stock_code, trade_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")

print("✅ 数据库和表创建完成")
conn.close()
```

### 4.3 插入数据

```python
import pymysql
from sqlalchemy import create_engine
import pandas as pd

# 使用 SQLAlchemy 批量写入（效率更高）
engine = create_engine('mysql+pymysql://root:your_password@localhost/quant_db?charset=utf8mb4')

# 插入数据（REPLACE 模式：若已存在则更新）
for code, df in all_data.items():
    # 重命名列以匹配数据库结构
    df_renamed = df.rename(columns={
        '日期': 'trade_date',
        '开盘': 'open',
        '最高': 'high',
        '最低': 'low',
        '收盘': 'close',
        '成交量': 'volume',
        '成交额': 'amount'
    })
    df_renamed['stock_code'] = code

    # 写入数据库
    df_renamed.to_sql('stock_daily', engine, if_exists='replace', index=False)
    print(f"📦 {code} 数据已保存: {len(df_renamed)} 条")

engine.dispose()
print("\n✅ 数据保存完成: MySQL quant_db.stock_daily")
```

---

## 5. 数据验证

```python
import pymysql

# 连接 MySQL
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='quant_db',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 查看所有表
cursor.execute("SHOW TABLES")
print("数据库表:", cursor.fetchall())

# 检查各股票记录数
cursor.execute("""
    SELECT stock_code, COUNT(*) as count, MIN(trade_date), MAX(trade_date)
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
A股历史K线数据获取脚本（MySQL 版本）
"""
import akshare as ak
import pandas as pd
from sqlalchemy import create_engine

# MySQL 连接配置（根据你的环境修改）
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'quant_db',
    'charset': 'utf8mb4'
}

def fetch_stock_daily(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取单只股票历史日K线"""
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
    return df

def init_database():
    """初始化数据库和表"""
    import pymysql

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_daily (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_code VARCHAR(20) NOT NULL,
            trade_date DATE NOT NULL,
            open DECIMAL(10, 2),
            high DECIMAL(10, 2),
            low DECIMAL(10, 2),
            close DECIMAL(10, 2),
            volume DECIMAL(20, 2),
            amount DECIMAL(20, 2),
            UNIQUE KEY uk_code_date (stock_code, trade_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

def save_to_mysql(data_dict: dict):
    """保存股票数据到 MySQL"""
    engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset=utf8mb4")

    for code, df in data_dict.items():
        df_copy = df.copy()
        df_copy['stock_code'] = code
        df_copy.to_sql('stock_daily', engine, if_exists='replace', index=False)
        print(f"📦 {code} 已保存: {len(df)} 条")

    engine.dispose()
    print("✅ 保存完成: MySQL quant_db.stock_daily")

if __name__ == "__main__":
    # 初始化数据库
    init_database()

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

    save_to_mysql(all_data)
```

---

## 7. 今日成果

完成今天的学习后，你将：
1. 掌握使用 akshare 获取 A 股历史K线和实时行情
2. 学会将数据存储到 MySQL 数据库
3. 拥有可复用的数据获取脚本
4. 为明天的数据存储方案设计做好准备

---

## 常见问题

**Q: 获取数据报错 "请求过于频繁"**
> akshare 有频率限制，在循环中添加延时：
> `import time; time.sleep(1)`

**Q: 某些股票没有数据**
> 检查股票代码是否正确，或尝试获取更短的时间范围

**Q: MySQL 连接报错 "Access denied"**
> 检查密码是否正确，或使用以下命令测试连接：
> `mysql -u root -p`

**Q: 如何用命令行查看 MySQL 数据**
> ```bash
> mysql -u root -p quant_db
> SELECT * FROM stock_daily LIMIT 5;
> ```
