# 第 1 周 · 第 4 天：数据流程整合与批量获取

> 目标：整合数据层，实现批量获取多只股票数据，验证完整数据流程

---

## 1. 今日任务清单

- [ ] 完善数据获取脚本 `fetch_stock_data.py`
- [ ] 实现批量获取股票数据
- [ ] 添加数据去重和增量更新逻辑
- [ ] 添加进度显示
- [ ] 测试完整数据流程

---

## 2. 整合数据层

`data/database.py` 已完成，今天将其与 `fetch_data.py` 整合成完整的数据获取工具。

### 2.1 完整的股票数据获取脚本

创建 `data/fetch_stock_data.py`：

```python
"""
data/fetch_stock_data.py
========================
A股股票数据批量获取工具
"""
import akshare as ak
import pandas as pd
import time
from datetime import datetime
from data.database import StockDataDB


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

        symbol = stock_code.replace(".SZ", "").replace(".SH", "")

        if show_progress:
            print(f"📥 正在获取 {stock_code}...")

        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date
            )

            if len(df) > 0:
                # 保存到数据库
                self.db.save_daily_data(df, stock_code)

                if show_progress:
                    print(f"   ✅ {stock_code}: {len(df)} 条数据")

                return df
            else:
                if show_progress:
                    print(f"   ⚠️ {stock_code}: 无数据")
                return pd.DataFrame()

        except Exception as e:
            if show_progress:
                print(f"   ❌ {stock_code}: {str(e)}")
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
            print(f"[{i}/{total}] ", end="")
            df = self.fetch_single(code, start_date, end_date, show_progress=False)
            results[code] = df

            # 进度显示
            if len(df) > 0:
                print(f"[{i}/{total}] ✅ {code}: {len(df)} 条")
            else:
                print(f"[{i}/{total}] ⚠️ {code}: 无数据")

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
        # 获取行业股票列表
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

    # 方式2: 自定义股票列表
    # results = fetcher.fetch_batch(
    #     stock_codes=["000001.SZ", "600519.SH"],
    #     start_date="20230101"
    # )

    # 验证数据
    print("\n📊 数据验证:")
    df = fetcher.db.get_daily_data("000001.SZ", start_date="20260101")
    print(f"000001.SZ 最新数据: {len(df)} 条")
    print(df.tail(3))
```

---

## 3. 数据增量更新

创建 `data/update_data.py`，实现增量更新：

```python
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
            from datetime import datetime
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


if __name__ == "__main__":
    update_all()
```

---

## 4. 完整使用流程

### 步骤1: 初始化数据库

```bash
cd learn-stock
python -c "from data.database import StockDataDB; db = StockDataDB(); db.init_tables()"
```

### 步骤2: 首次全量获取（获取近3年数据）

```python
from data.fetch_stock_data import StockDataFetcher, STOCK_POOLS

fetcher = StockDataFetcher()
results = fetcher.fetch_batch(
    stock_codes=STOCK_POOLS["sample"],
    start_date="20230101",
    delay=1.5  # 1.5秒间隔，避免限流
)
```

### 步骤3: 每日增量更新

```python
from data.update_data import update_all

update_all()  # 自动更新所有股票最近30天数据
```

### 步骤4: 验证数据

```python
from data.database import StockDataDB

db = StockDataDB()

# 查看所有股票
cursor.execute("SELECT stock_code, COUNT(*) as cnt FROM stock_daily GROUP BY stock_code")
for row in cursor.fetchall():
    print(f"{row['stock_code']}: {row['cnt']} 条")

# 读取单只股票数据
df = db.get_daily_data("000001.SZ", start_date="20260101")
print(df.tail())
```

---

## 5. 今日成果

完成今天的学习后，你将：
1. 拥有完整的股票数据获取工具链
2. 支持批量获取多只股票
3. 支持增量更新，避免重复获取
4. 为第2周金融市场学习和后续回测准备好数据

---

## 常见问题

**Q: 请求被限流怎么办？**
> 增大 `delay` 参数，建议 1.5-2.0 秒

**Q: 某些股票数据缺失？**
> A股有停牌制度，使用 `update_all(days_back=60)` 补充更多历史数据

**Q: 如何获取全市场股票？**
> 使用 `akshare` 的股票列表接口：
> `ak.stock_zh_a_spot_em()` 获取所有股票代码
