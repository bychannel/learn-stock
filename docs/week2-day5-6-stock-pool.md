# 第 2 周 · 第 5-6 天：选股池构建实战

> 目标：构建自己的 10 只股票选股池，采集关键财务指标，形成可复用的选股代码
> 完成日期：2026-07-01

---

## 1. 选股池构建流程

```
确定投资偏好 → 行业选择 → 财务筛选 → 技术面验证 → 最终确认
```

### 投资风格分类

| 风格 | 特点 | 适合指标 |
|------|------|----------|
| 价值投资 | 长期持有，追求稳定收益 | 低 PE、低 PB、高 ROE |
| 成长投资 | 追求高增长 | 高营收增速、高净利润增速 |
| 趋势投资 | 跟势操作 | 均线多头排列、换手率适中 |
| 指数投资 | 复制指数 | 选择主要宽基成分股 |

---

## 2. 行业选择建议

建议选择 2-3 个自己熟悉的行业，分散风险：

| 行业 | 特点 | 优质指标 |
|------|------|----------|
| 银行 | 低估值、高股息、稳定 | PB、股息率 |
| 白酒 | 高毛利、高 ROE | 毛利率、营收增速 |
| 消费 | 稳定、抗周期 | ROE、现金流 |
| 医药 | 成长性强 | 营收增速、研发投入 |
| 科技 | 高增长、高波动 | 营收增速、市场份额 |

---

## 3. 财务数据采集代码

```python
import akshare as ak
import pandas as pd

def get_stock_pool_financial(stock_list):
    """
    获取选股池股票的财务指标
    Args:
        stock_list: [(代码, 名称, 行业), ...]
    Returns:
        DataFrame: 包含财务指标的表格
    """
    results = []
    for code, name, industry in stock_list:
        try:
            df_finance = ak.stock_financial_analysis_indicator(symbol=code)
            df_finance = df_finance.sort_values('日期', ascending=False)

            df_spot = ak.stock_zh_a_spot_em()
            spot = df_spot[df_spot['代码'] == code].iloc[0]
            latest = df_finance.iloc[0]

            results.append({
                '股票代码': code,
                '股票名称': name,
                '行业': industry,
                '最新价': spot['最新价'],
                '涨跌幅': spot['涨跌幅'],
                '市盈率-动态': spot.get('市盈率-动态', None),
                '市净率': spot.get('市净率', None),
                '总市值': spot.get('总市值', None),
                'ROE(%)': latest.get('净资产收益率(%)', None),
                '毛利率(%)': latest.get('销售毛利率(%)', None),
                '净利率(%)': latest.get('销售净利率(%)', None),
                '资产负债率(%)': latest.get('资产负债率(%)', None),
            })
            print(f"✅ {code} {name} 获取成功")
        except Exception as e:
            print(f"❌ {code} {name} 获取失败: {e}")

    return pd.DataFrame(results)
```

---

## 4. 选股池示例（10只股票）

```python
my_stock_pool = [
    # 银行板块（3只）
    ("600036", "招商银行", "银行"),
    ("601166", "兴业银行", "银行"),
    ("000001", "平安银行", "银行"),

    # 白酒板块（2只）
    ("600519", "贵州茅台", "白酒"),
    ("000858", "五粮液", "白酒"),

    # 消费板块（2只）
    ("600887", "伊利股份", "食品饮料"),
    ("000895", "双汇发展", "食品饮料"),

    # 医药板块（1只）
    ("600276", "恒瑞医药", "医药"),

    # 科技板块（2只）
    ("300750", "宁德时代", "新能源"),
    ("688981", "中芯国际", "半导体"),
]

df_pool = get_stock_pool_financial(my_stock_pool)
```

---

## 5. 选股池分析维度

### 估值分析
- PE（市盈率）：越低越便宜
- PB（市净率）：破净股值得关注

### 盈利能力分析
- ROE：> 10% 为优质，> 20% 为优秀
- 毛利率：> 20% 为良好，> 40% 为极强
- 净利率：> 10% 为良好

### 财务风险分析
- 资产负债率：< 70% 为安全

### 规模分析
- 总市值：> 100 亿为大盘股，稳定性好

---

## 6. 保存选股池

```python
import os
os.makedirs('reports', exist_ok=True)

# 保存到 CSV
df_pool.to_csv('reports/stock_pool_w2.csv', index=False, encoding='utf-8-sig')

# 保存到 MySQL
from data.database import StockDataDB
db = StockDataDB()

for _, row in df_pool.iterrows():
    suffix = '.SH' if row['股票代码'].startswith(('6', '5')) else '.SZ'
    db.save_stock_info(
        stock_code=row['股票代码'] + suffix,
        stock_name=row['股票名称'],
        market='SH' if row['股票代码'].startswith(('6', '5')) else 'SZ',
        industry=row['行业']
    )
```

---

## 7. 今日任务清单

- [x] 确定自己的投资偏好（价值/成长/趋势）
- [x] 选择 2-3 个熟悉的行业
- [x] 选出 10 只股票构建选股池
- [x] 采集选股池的关键财务指标
- [x] 将选股池保存到 CSV 和 MySQL
- [x] 编写定期更新代码

---

## ✅ 今日要点总结

1. **选股池构建原则**：行业分散、财务稳健、估值合理
2. **核心指标**：PE、PB、ROE、毛利率、资产负债率
3. **数据来源**：akshare 实时行情 + 财务指标
4. **保存方式**：CSV（方便查看）+ MySQL（方便程序调用）

---

## 下一步

第二周 第 7 天 - 周末输出（选股池表格 + 数据采集代码整理）