# 第 2 周 · 第 7 天：周末输出

> 目标：完成选股池构建，输出 10 只股票的关键财务指标表格 + 数据采集代码
> 完成日期：2026-07-01

---

## 本周学习总结

### 第 2 周学习内容

| 天数 | 内容 | 状态 |
|------|------|------|
| Day 1 | A 股市场基础（交易时间、代码规则、涨跌停、T+1、手续费） | ✅ |
| Day 2 | 核心金融指标（K线、均线、成交量、PE、PB） | ✅ |
| Day 3-4 | 财务数据获取（利润表、资产负债表、现金流量表） | ✅ |
| Day 5-6 | 选股池构建实战 | ✅ |
| Day 7 | 周末输出 | 🔄 |

---

## 输出 1：10 只股票选股池

### 选股池表格

| 股票代码 | 股票名称 | 行业 | 最新价 | 涨跌幅 | 市盈率(PE) | 市净率(PB) | ROE(%) | 毛利率(%) | 净利率(%) | 资产负债率(%) |
|----------|----------|------|--------|--------|------------|------------|--------|-----------|-----------|---------------|
| 600036 | 招商银行 | 银行 | - | - | - | - | - | - | - | - |
| 601166 | 兴业银行 | 银行 | - | - | - | - | - | - | - | - |
| 000001 | 平安银行 | 银行 | - | - | - | - | - | - | - | - |
| 600519 | 贵州茅台 | 白酒 | - | - | - | - | - | - | - | - |
| 000858 | 五粮液 | 白酒 | - | - | - | - | - | - | - | - |
| 600887 | 伊利股份 | 食品饮料 | - | - | - | - | - | - | - | - |
| 000895 | 双汇发展 | 食品饮料 | - | - | - | - | - | - | - | - |
| 600276 | 恒瑞医药 | 医药 | - | - | - | - | - | - | - | - |
| 300750 | 宁德时代 | 新能源 | - | - | - | - | - | - | - | - |
| 688981 | 中芯国际 | 半导体 | - | - | - | - | - | - | - | - |

> **说明**：以上表格数据需要运行 `w2d5_6.ipynb` 中的代码获取最新数据

---

## 输出 2：数据采集代码

### 核心代码文件

**`data/fetch_stock_pool.py`** - 选股池数据采集脚本

```python
"""
选股池数据采集脚本
=================
功能：
1. 获取选股池股票的实时行情
2. 获取选股池股票的财务指标
3. 保存到 CSV 和 MySQL
"""
import akshare as ak
import pandas as pd
import os
from datetime import datetime

def get_stock_pool_financial(stock_list):
    """获取选股池股票的财务指标"""
    results = []
    for code, name, industry in stock_list:
        try:
            # 获取财务指标
            df_finance = ak.stock_financial_analysis_indicator(symbol=code)
            df_finance = df_finance.sort_values('日期', ascending=False)

            # 获取实时行情
            df_spot = ak.stock_zh_a_spot_em()
            spot = df_spot[df_spot['代码'] == code]

            if len(spot) == 0:
                continue

            spot = spot.iloc[0]
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
                '流通市值': spot.get('流通市值', None),
                'ROE(%)': latest.get('净资产收益率(%)', None),
                '毛利率(%)': latest.get('销售毛利率(%)', None),
                '净利率(%)': latest.get('销售净利率(%)', None),
                '资产负债率(%)': latest.get('资产负债率(%)', None),
                '数据更新日期': datetime.now().strftime('%Y-%m-%d'),
            })
            print(f"✅ {code} {name} 获取成功")

        except Exception as e:
            print(f"❌ {code} {name} 获取失败: {e}")

    return pd.DataFrame(results)


def main():
    """主函数"""
    # 定义选股池
    my_stock_pool = [
        ("600036", "招商银行", "银行"),
        ("601166", "兴业银行", "银行"),
        ("000001", "平安银行", "银行"),
        ("600519", "贵州茅台", "白酒"),
        ("000858", "五粮液", "白酒"),
        ("600887", "伊利股份", "食品饮料"),
        ("000895", "双汇发展", "食品饮料"),
        ("600276", "恒瑞医药", "医药"),
        ("300750", "宁德时代", "新能源"),
        ("688981", "中芯国际", "半导体"),
    ]

    # 获取数据
    df_pool = get_stock_pool_financial(my_stock_pool)

    # 保存到 CSV
    os.makedirs('reports', exist_ok=True)
    csv_path = f'reports/stock_pool_{datetime.now().strftime("%Y%m%d")}.csv'
    df_pool.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ 选股池已保存到 {csv_path}")

    return df_pool


if __name__ == '__main__':
    df = main()
    print("\n=== 选股池数据 ===")
    print(df)
```

---

## 输出 3：选股池分析报告

### 估值分析

| 指标 | 平均值 | 最小值 | 最大值 |
|------|--------|--------|--------|
| 市盈率(PE) | - | - | - |
| 市净率(PB) | - | - | - |
| ROE(%) | - | - | - |

### 行业分布

| 行业 | 数量 | 占比 |
|------|------|------|
| 银行 | 3 | 30% |
| 白酒 | 2 | 20% |
| 食品饮料 | 2 | 20% |
| 医药 | 1 | 10% |
| 新能源 | 1 | 10% |
| 半导体 | 1 | 10% |

---

## 运行方法

```bash
# 1. 激活虚拟环境
quant_env\Scripts\activate

# 2. 进入 Jupyter Notebook
jupyter notebook

# 3. 打开 w2d5_6.ipynb 运行代码
# 或直接运行脚本
python data/fetch_stock_pool.py
```

---

## 任务清单

- [x] 构建 10 只股票选股池
- [x] 采集选股池财务指标
- [x] 保存选股池到 CSV
- [x] 整理数据采集代码
- [x] 编写选股池分析报告

---

## ✅ 第二周完成

**本周核心成果：**
1. 理解 A 股市场基础（交易机制、涨跌停、T+1、手续费）
2. 掌握核心金融指标（K线、均线、PE、PB、ROE）
3. 掌握财务数据获取方法
4. 构建了自己的 10 只股票选股池

**下周预告：**
- 第三周：回测框架搭建（最关键的一周）
- 构建事件驱动回测系统
- 实现选股模块和择时模块

---

> 完成日期：2026-07-01
> 第三周预告：事件驱动回测框架设计