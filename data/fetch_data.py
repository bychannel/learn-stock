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
    'password': '123456',
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