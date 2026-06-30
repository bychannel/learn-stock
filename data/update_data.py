"""
data/update_data.py
===================
增量更新股票数据（只更新数据库中不存在的日期）
"""
from datetime import datetime, timedelta
from data.database import StockDataDB
from data.fetch_stock_data import StockDataFetcher, STOCK_POOLS


def get_latest_date(stock_code: str, db: StockDataDB) -> str:
    """获取数据库中某股票最新日期"""
    import pymysql

    conn = pymysql.connect(**db.config)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(trade_date) FROM stock_daily
        WHERE stock_code = %s
    """, (stock_code,))

    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        # 返回下一天，作为增量更新的起点
        latest = result[0]
        if isinstance(latest, str):
            latest = datetime.strptime(latest, "%Y-%m-%d")

        next_day = latest + timedelta(days=1)
        return next_day.strftime("%Y%m%d")
    else:
        # 数据库中没有，从2023年开始
        return "20230101"


def update_all(stock_pool: list = None, days_back: int = 30):
    """
    更新所有股票数据

    Args:
        stock_pool: 股票列表，默认使用 sample 池
        days_back: 保留最近多少天的数据（应对停牌期间的数据缺失）
    """
    db = StockDataDB()
    fetcher = StockDataFetcher(db)

    if stock_pool is None:
        stock_pool = STOCK_POOLS["sample"]

    # 计算更新起点（最近 N 天前，确保覆盖停牌期间）
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")

    print(f"\n增量更新模式: {start_date} 至今")
    print(f"更新股票数: {len(stock_pool)}")

    for code in stock_pool:
        # 获取该股票在数据库中的最新日期
        latest = get_latest_date(code, db)

        # 如果数据库已有最新数据，从数据库最新日期的下一天开始
        if latest != start_date:
            print(f"\n📥 更新 {code}: {latest} 至今")
            fetcher.fetch_single(code, latest, show_progress=True)
        else:
            print(f"⏭️ {code}: 已是最新")

    print("\n✅ 增量更新完成")


def get_data_status() -> dict:
    """获取数据库中各股票的数据状态"""
    import pymysql
    from data.database import DB_CONFIG

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT
            stock_code,
            COUNT(*) as total_count,
            MIN(trade_date) as start_date,
            MAX(trade_date) as end_date
        FROM stock_daily
        GROUP BY stock_code
        ORDER BY stock_code
    """)

    results = cursor.fetchall()
    conn.close()

    return results


if __name__ == "__main__":
    # 显示数据状态
    print("📊 数据库数据状态:")
    status = get_data_status()
    for s in status:
        print(f"  {s['stock_code']}: {s['total_count']} 条 ({s['start_date']} ~ {s['end_date']})")

    # 执行增量更新
    print("\n" + "="*50)
    update_all()
