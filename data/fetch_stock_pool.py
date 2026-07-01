"""
选股池数据采集脚本
=================
功能：
1. 获取选股池股票的实时行情
2. 获取选股池股票的财务指标
3. 保存到 CSV 和 MySQL

使用方法：
    python data/fetch_stock_pool.py
"""
import akshare as ak
import pandas as pd
import os
from datetime import datetime


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
            # 获取财务指标
            df_finance = ak.stock_financial_analysis_indicator(symbol=code)
            df_finance = df_finance.sort_values('日期', ascending=False)

            # 获取实时行情
            df_spot = ak.stock_zh_a_spot_em()
            spot = df_spot[df_spot['代码'] == code]

            if len(spot) == 0:
                print(f"⚠️ {code} {name} 未找到实时行情数据")
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


def save_to_csv(df, filename=None):
    """保存到 CSV 文件"""
    if filename is None:
        filename = f'stock_pool_{datetime.now().strftime("%Y%m%d")}.csv'

    os.makedirs('reports', exist_ok=True)
    csv_path = os.path.join('reports', filename)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ 选股池已保存到 {csv_path}")
    return csv_path


def main():
    """主函数"""
    # 定义选股池（可根据需要修改）
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

    print("=" * 50)
    print("选股池数据采集")
    print("=" * 50)
    print(f"股票数量: {len(my_stock_pool)}")
    print(f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 获取数据
    df_pool = get_stock_pool_financial(my_stock_pool)

    if len(df_pool) > 0:
        # 保存到 CSV
        save_to_csv(df_pool)

        # 打印统计信息
        print("\n" + "=" * 50)
        print("选股池统计")
        print("=" * 50)

        # 估值统计
        pe_valid = df_pool[df_pool['市盈率-动态'] > 0]['市盈率-动态']
        pb_valid = df_pool[df_pool['市净率'] > 0]['市净率']
        roe_valid = df_pool[df_pool['ROE(%)'] > 0]['ROE(%)']

        if len(pe_valid) > 0:
            print(f"市盈率(PE): 平均 {pe_valid.mean():.2f}, 范围 {pe_valid.min():.2f} ~ {pe_valid.max():.2f}")
        if len(pb_valid) > 0:
            print(f"市净率(PB): 平均 {pb_valid.mean():.2f}, 范围 {pb_valid.min():.2f} ~ {pb_valid.max():.2f}")
        if len(roe_valid) > 0:
            print(f"ROE: 平均 {roe_valid.mean():.2f}%, 范围 {roe_valid.min():.2f}% ~ {roe_valid.max():.2f}%")

        # 行业分布
        print("\n行业分布:")
        industry_counts = df_pool['行业'].value_counts()
        for industry, count in industry_counts.items():
            print(f"  {industry}: {count} 只")

        # 打印完整表格
        print("\n" + "=" * 50)
        print("选股池完整数据")
        print("=" * 50)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(df_pool)

    else:
        print("❌ 未获取到任何数据")

    return df_pool


if __name__ == '__main__':
    df = main()