"""
data/fetch_stock_data.py
========================
A股股票数据批量获取工具
"""
import sys
import os

# 将项目根目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import akshare as ak
import pandas as pd
import time
from datetime import datetime
from data.database import StockDataDB


def fetch_single_stock(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取单只股票历史日K线（使用新浪接口）

    Args:
        stock_code: 股票代码，如 "000001.SZ"
        start_date: 开始日期，如 "20230101"
        end_date: 结束日期，如 "20260630"

    Returns:
        DataFrame
    """
    # 转换代码格式：000001.SZ -> sz000001
    symbol = stock_code.replace(".SZ", "").replace(".SH", "")
    prefix = "sz" if stock_code.endswith(".SZ") else "sh"

    # 使用新浪接口获取数据
    df = ak.stock_zh_a_daily(
        symbol=f"{prefix}{symbol}",
        start_date=start_date.replace("-", ""),
        end_date=end_date.replace("-", "")
    )

    return df


class StockDataFetcher:
    """股票数据获取器"""

    def __init__(self, db: StockDataDB = None):
        self.db = db or StockDataDB()
        self.db.init_tables()

    def fetch_single(
        self,
        stock_code: str,
        start_date: str,
        end_date: str = None,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        获取单只股票历史数据

        Args:
            stock_code: 股票代码，如 "000001.SZ"
            start_date: 开始日期，如 "20230101"
            end_date: 结束日期，默认今天
            show_progress: 是否显示进度

        Returns:
            DataFrame
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        if show_progress:
            print(f"[GET] Fetching {stock_code}...")

        try:
            df = fetch_single_stock(stock_code, start_date, end_date)

            if len(df) > 0:
                # 保存到数据库
                self.db.save_daily_data(df, stock_code)

                if show_progress:
                    print(f"   [OK] {stock_code}: {len(df)} records")

                return df
            else:
                if show_progress:
                    print(f"   [WARN] {stock_code}: No data")
                return pd.DataFrame()

        except Exception as e:
            if show_progress:
                print(f"   [ERROR] {stock_code}: {str(e)}")
            return pd.DataFrame()

    def fetch_batch(
        self,
        stock_codes: list,
        start_date: str,
        end_date: str = None,
        delay: float = 1.0
    ) -> dict:
        """
        批量获取多只股票数据

        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            delay: 请求间隔（秒），避免频率限制

        Returns:
            dict: {stock_code: DataFrame}
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")

        results = {}
        total = len(stock_codes)

        print(f"\n{'='*50}")
        print(f"开始批量获取 {total} 只股票数据")
        print(f"时间范围: {start_date} ~ {end_date}")
        print(f"{'='*50}\n")

        for i, code in enumerate(stock_codes, 1):
            df = self.fetch_single(code, start_date, end_date, show_progress=False)
            results[code] = df

            # 进度显示
            if len(df) > 0:
                print(f"[{i}/{total}] [OK] {code}: {len(df)} records")
            else:
                print(f"[{i}/{total}] [WARN] {code}: No data")

            # 请求间隔，避免被限流
            if i < total:
                time.sleep(delay)

        # 统计
        success = sum(1 for df in results.values() if len(df) > 0)
        print(f"\n{'='*50}")
        print(f"批量获取完成: {success}/{total} 只成功")
        print(f"{'='*50}")

        return results

    def fetch_by_industry(self, industry: str, **kwargs) -> dict:
        """获取指定行业的所有股票"""
        df = ak.stock_board_industry_cons_em(symbol=industry)
        codes = df['代码'].tolist()[:10]  # 限制数量，避免请求过多
        return self.fetch_batch(codes, **kwargs)


# ========== 预定义股票池 ==========

STOCK_POOLS = {
    # 金融板块
    "finance": [
        "000001.SZ",  # 平安银行
        "600000.SH",  # 浦发银行
        "600036.SH",  # 招商银行
        "601166.SH",  # 兴业银行
        "600016.SH",  # 民生银行
    ],
    # 消费板块
    "consumer": [
        "600519.SH",  # 贵州茅台
        "000858.SZ",  # 五粮液
        "000568.SZ",  # 泸州老窖
        "600887.SH",  # 伊利股份
        "002304.SZ",  # 洋河股份
    ],
    # 科技板块
    "tech": [
        "000002.SZ",  # 万科A
        "600030.SH",  # 中信证券
        "601318.SH",  # 中国平安
        "600276.SH",  # 恒瑞医药
        "300750.SZ",  # 宁德时代
    ],
    # 全市场示例
    "sample": [
        "000001.SZ",  # 平安银行
        "600000.SH",  # 浦发银行
        "600519.SH",  # 贵州茅台
        "000858.SZ",  # 五粮液
        "600036.SH",  # 招商银行
        "601166.SH",  # 兴业银行
        "600016.SH",  # 民生银行
        "000568.SZ",  # 泸州老窖
        "600887.SH",  # 伊利股份
        "002304.SZ",  # 洋河股份
    ]
}


if __name__ == "__main__":
    # 创建数据获取器
    fetcher = StockDataFetcher()

    # 方式1: 使用预定义股票池
    print("使用预定义股票池 (sample)...")
    results = fetcher.fetch_batch(
        stock_codes=STOCK_POOLS["sample"],
        start_date="20230101",
        delay=1.0
    )

    # 验证数据
    print("\n[INFO] Data verification:")
    df = fetcher.db.get_daily_data("000001.SZ", start_date="20260101")
    print(f"000001.SZ 最新数据: {len(df)} 条")
    if len(df) > 0:
        print(df.tail(3))
