# 第 1 周 · 第 3 天：数据存储方案设计

> 目标：设计并实现标准化的 K 线数据表结构，实现数据层抽象

---

## 1. 今日任务清单

- [ ] 设计股票基础信息表
- [ ] 设计日K线数据表（已创建）
- [ ] 实现数据层封装
- [ ] 实现数据读取接口
- [ ] 编写单元测试验证

---

## 2. 数据库表结构设计

根据 A 股数据特点，设计以下表结构：

### 2.1 股票基础信息表

```sql
-- 创建股票基础信息表
CREATE TABLE IF NOT EXISTS stock_info (
    stock_code VARCHAR(20) PRIMARY KEY COMMENT '股票代码 如: 000001.SZ',
    stock_name VARCHAR(50) NOT NULL COMMENT '股票名称',
    market VARCHAR(10) NOT NULL COMMENT '市场: SZ/SH',
    industry VARCHAR(50) COMMENT '所属行业',
    list_date DATE COMMENT '上市日期',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用: 1是 0否',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基础信息表';
```

### 2.2 日K线数据表（完善版）

```sql
-- 完善日K线表，添加更多字段
CREATE TABLE IF NOT EXISTS stock_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open DECIMAL(10, 3) COMMENT '开盘价',
    high DECIMAL(10, 3) COMMENT '最高价',
    low DECIMAL(10, 3) COMMENT '最低价',
    close DECIMAL(10, 3) COMMENT '收盘价',
    volume DECIMAL(20, 2) COMMENT '成交量(手)',
    amount DECIMAL(20, 2) COMMENT '成交额(元)',
    amplitude DECIMAL(10, 3) COMMENT '振幅(%)',
    change_pct DECIMAL(10, 3) COMMENT '涨跌幅(%)',
    change_amount DECIMAL(10, 3) COMMENT '涨跌额',
    turnover_rate DECIMAL(10, 4) COMMENT '换手率(%)',
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_stock_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日K线数据表';
```

---

## 3. 数据层封装

创建 `data/database.py`，实现数据访问层：

```python
"""
data/database.py
=================
数据访问层封装
"""
import pymysql
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import pandas as pd

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'quant_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor  # 返回字典而非元组
}


@contextmanager
def get_connection():
    """获取数据库连接的上下文管理器"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


class StockDataDB:
    """股票数据数据库操作类"""

    def __init__(self):
        self.config = DB_CONFIG

    def init_tables(self):
        """初始化数据库表"""
        with get_connection() as conn:
            cursor = conn.cursor()

            # 股票基础信息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_info (
                    stock_code VARCHAR(20) PRIMARY KEY,
                    stock_name VARCHAR(50) NOT NULL,
                    market VARCHAR(10) NOT NULL,
                    industry VARCHAR(50),
                    list_date DATE,
                    is_enabled TINYINT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # 日K线数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_daily (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    stock_code VARCHAR(20) NOT NULL,
                    trade_date DATE NOT NULL,
                    open DECIMAL(10, 3),
                    high DECIMAL(10, 3),
                    low DECIMAL(10, 3),
                    close DECIMAL(10, 3),
                    volume DECIMAL(20, 2),
                    amount DECIMAL(20, 2),
                    amplitude DECIMAL(10, 3),
                    change_pct DECIMAL(10, 3),
                    change_amount DECIMAL(10, 3),
                    turnover_rate DECIMAL(10, 4),
                    UNIQUE KEY uk_code_date (stock_code, trade_date),
                    INDEX idx_trade_date (trade_date),
                    INDEX idx_stock_code (stock_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            conn.commit()
            print("✅ 数据库表初始化完成")

    def save_daily_data(self, df: pd.DataFrame, stock_code: str):
        """保存日K线数据"""
        df_copy = df.copy()
        df_copy['stock_code'] = stock_code

        # 添加计算字段
        if '涨跌幅' in df_copy.columns:
            df_copy['change_pct'] = df_copy['涨跌幅']
        if '涨跌额' in df_copy.columns:
            df_copy['change_amount'] = df_copy['涨跌额']

        with get_connection() as conn:
            df_copy.to_sql('stock_daily', conn, if_exists='replace', index=False)
            print(f"📦 {stock_code} 保存成功: {len(df_copy)} 条")

    def get_daily_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """读取日K线数据"""
        sql = "SELECT * FROM stock_daily WHERE stock_code = %s"
        params = [stock_code]

        if start_date:
            sql += " AND trade_date >= %s"
            params.append(start_date)
        if end_date:
            sql += " AND trade_date <= %s"
            params.append(end_date)

        sql += " ORDER BY trade_date"

        with get_connection() as conn:
            df = pd.read_sql(sql, conn, params=params)
            return df

    def get_stock_list(self, market: Optional[str] = None) -> List[Dict]:
        """获取股票列表"""
        sql = "SELECT * FROM stock_info WHERE is_enabled = 1"
        if market:
            sql += " AND market = %s"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (market,) if market else None)
            return cursor.fetchall()

    def save_stock_info(self, stock_code: str, stock_name: str, market: str, **kwargs):
        """保存股票基础信息"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stock_info (stock_code, stock_name, market, industry, list_date)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    stock_name = VALUES(stock_name),
                    industry = VALUES(industry),
                    list_date = VALUES(list_date)
            """, (stock_code, stock_name, market, kwargs.get('industry'), kwargs.get('list_date')))
            conn.commit()
```

---

## 4. 数据层使用示例

```python
from data.database import StockDataDB

# 初始化数据库
db = StockDataDB()
db.init_tables()

# 获取数据（示例：需要先通过 akshare 获取）
import akshare as ak

# 获取平安银行数据
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20250630", end_date="20260630")
print(f"获取数据: {len(df)} 条")
print(df.head())

# 保存到数据库
db.save_daily_data(df, "000001.SZ")

# 从数据库读取
df_from_db = db.get_daily_data("000001.SZ", start_date="20260101")
print(f"\n从数据库读取: {len(df_from_db)} 条")
print(df_from_db.head())
```

---

## 5. 完整项目结构

今天的代码应形成如下结构：

```
data/
├── __init__.py
├── database.py      # 数据访问层
├── fetch_data.py    # 数据获取
└── stock_data.db    # MySQL 数据库

backtest/
strategies/
reports/
```

创建 `data/__init__.py`：

```python
"""data package"""
from .database import StockDataDB, get_connection

__all__ = ['StockDataDB', 'get_connection']
```

---

## 6. 今日成果

完成今天的学习后，你将：
1. 掌握 MySQL 数据库表设计
2. 实现数据访问层封装
3. 拥有可复用的数据读写接口
4. 为后续回测系统提供统一数据源

---

## 常见问题

**Q: 如何查看 MySQL 中的数据量？**
> ```sql
> SELECT COUNT(*) FROM stock_daily;
> SELECT stock_code, COUNT(*) FROM stock_daily GROUP BY stock_code;
> ```

**Q: 数据量大了查询慢怎么办？**
> 添加索引，当前表已有 `trade_date` 和 `stock_code` 索引

**Q: 如何定期更新数据？**
> 使用 pandas 的 `merge` 或 `INSERT ... ON DUPLICATE KEY UPDATE`
