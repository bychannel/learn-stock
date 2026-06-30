"""
data/database.py
=================
数据访问层封装
"""
import pymysql
from sqlalchemy import create_engine
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import pandas as pd

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'quant_db',
    'charset': 'utf8mb4',
}

# SQLAlchemy 引擎（用于 pandas to_sql）
engine = create_engine(
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
)


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
            print("[OK] Database tables initialized")

    def save_daily_data(self, df: pd.DataFrame, stock_code: str):
        """保存日K线数据"""
        df_copy = df.copy()
        df_copy['stock_code'] = stock_code

        # 列名映射（兼容新浪接口的英文列名）
        column_map = {
            'date': 'trade_date',      # 新浪接口
            '开盘': 'open',             # 东财接口
            '最高': 'high',             # 东财接口
            '最低': 'low',              # 东财接口
            '收盘': 'close',            # 东财接口
            '成交量': 'volume',         # 东财接口
            '成交额': 'amount',         # 东财接口
        }
        df_copy = df_copy.rename(columns=column_map)

        # 添加计算字段
        if '涨跌幅' in df_copy.columns:
            df_copy['change_pct'] = df_copy['涨跌幅']
        if '涨跌额' in df_copy.columns:
            df_copy['change_amount'] = df_copy['涨跌额']

        # 使用 SQLAlchemy 引擎
        df_copy.to_sql('stock_daily', engine, if_exists='replace', index=False)
        print(f"[OK] {stock_code} saved: {len(df_copy)} records")

    def get_daily_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """读取日K线数据"""
        conditions = ["stock_code = %s"]
        params = [stock_code]

        if start_date:
            conditions.append("trade_date >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("trade_date <= %s")
            params.append(end_date)

        sql = "SELECT * FROM stock_daily WHERE " + " AND ".join(conditions) + " ORDER BY trade_date"

        # 使用 tuple 作为 params
        df = pd.read_sql(sql, engine, params=tuple(params))
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