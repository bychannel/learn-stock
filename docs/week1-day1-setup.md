# 第 1 周 · 第 1 天：Python 环境搭建

> 目标：完成量化开发环境安装，验证数据获取工具可用

---

## 1. 安装 uv（跨平台 Python 包管理器）

uv 比 Anaconda 更快、更轻量，安装一次即可。

### Windows 系统

打开 **PowerShell**（非 CMD），执行：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装完成后**重启 PowerShell**，让环境变量生效。

### Linux / macOS 系统

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 2. 创建虚拟环境

在项目根目录下创建独立的 Python 环境：

```bash
# 创建虚拟环境（指定 Python 3.11）
uv venv quant_env --python 3.11

# 激活虚拟环境
# Windows:
quant_env\Scripts\activate
# Linux/macOS:
source quant_env/bin/activate
```

激活成功后，命令行前面会出现 `(quant_env)` 标记。

---

## 3. 安装核心依赖

```bash
uv pip install pandas numpy matplotlib seaborn plotly akshare jupyter
```

安装说明：
| 包 | 用途 |
|----|------|
| `pandas` | 数据分析核心 |
| `numpy` | 数值计算 |
| `matplotlib` | 基础图表 |
| `seaborn` | 统计图表 |
| `plotly` | 交互图表 |
| `akshare` | A 股数据获取 |
| `jupyter` | 交互式编程 |

---

## 4. 验证安装

启动 Jupyter Notebook：

```bash
jupyter notebook
```

浏览器会自动打开，在新建的 Notebook 中执行以下代码：

```python
import akshare as ak
import pandas as pd

# 测试 1：获取平安银行（000001.SZ）近一年日K线数据
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20250630", end_date="20260630")

print(f"数据形状: {df.shape}")
print(f"列名: {list(df.columns)}")
print(df.head())
```

**预期输出：** 能打印出包含日期、开盘、收盘、成交量等列的 DataFrame。

---

## 5. 目录结构初始化

在项目根目录下创建以下文件夹：

```bash
mkdir -p data backtest strategies reports
```

创建完成后，项目结构如下：

```
learn-stock/
├── data/        # 存放市场数据（SQLite）
├── backtest/    # 回测引擎代码
├── strategies/  # 策略代码
├── reports/     # 回测报告
└── quant_env/   # Python 虚拟环境
```

---

## 6. 今日任务清单

- [x] 安装 uv
- [x] 创建虚拟环境 `quant_env`
- [x] 激活虚拟环境
- [x] 安装全部依赖包
- [x] 启动 Jupyter Notebook
- [x] 运行 akshare 测试代码，获取一只股票历史数据
- [x] 创建 `data/` `backtest/` `strategies/` `reports/` 目录

---

## ✅ 完成任务

> 完成日期：2026-06-30

---

## 常见问题

**Q: Windows 上提示 "无法识别 uv 命令"**
> 重启 PowerShell 或重启电脑，让环境变量生效。

**Q: akshare 安装失败**
> 检查网络连接，或使用国内镜像：
> `uv pip install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple`

**Q: Jupyter 浏览器没自动打开**
> 手动打开浏览器，访问 http://localhost:8888

---

## 今日成果

完成今天的学习后，你将：
1. 拥有一个独立、可复现的 Python 量化开发环境
2. 验证了 akshare 数据获取工具正常工作
3. 为明天的数据获取任务做好了准备
