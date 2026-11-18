# 我的学习手册（mylesson）

欢迎！这里是为**零基础（只会一点 Python、没有股票知识）**的你量身准备的学习手册。

本项目 **EasyQuant（eqlib）** 是一个用 Python 编写的**中国 A 股事件驱动量化回测框架**。简单说：你写一段"买卖规则"（策略），它帮你用历史数据模拟"如果当年真的按这个规则交易，会赚还是亏"，并生成各种报表。

> 本手册只帮你"读懂代码、学会使用这个项目"，不涉及投资建议，也不保证策略盈利。

---

## 📚 本文件夹里的文档

| 文件 | 作用 | 什么时候读 |
|------|------|-----------|
| [01-学习规划.md](01-学习规划.md) | 从 0 到熟练的科学学习路线，分阶段、有任务和验收标准 | **先读这个**，它是总路线图 |
| [02-项目框架.md](02-项目框架.md) | 项目整体架构、数据流、目录结构、核心设计理念 | 学完 Python 基础后，正式动手前读 |
| [03-模块功能详解.md](03-模块功能详解.md) | 每个代码文件/模块的职责、关键 API、示例 | 当"字典"用，用到哪个模块查哪个 |

---

## 🗺️ 建议阅读顺序

```
第 1 步  读 01-学习规划.md
         ↓
第 2 步  按规划里的"阶段 0/1"装环境、补 Python 数据工具（pandas/numpy）
         ↓
第 3 步  读 02-项目框架.md —— 建立项目全貌
         ↓
第 4 步  读 03-模块功能详解.md —— 按需查模块
         ↓
第 5 步  跟着 examples/ 目录的 25 个示例，从 01 写到 25
```

---

## ⚡ 一分钟快速上手（先感受一下）

```bash
# 1. 安装（在项目根目录）
pip install -e ".[dev]"

# 2. 确认库可用
python -c "from eqlib import *; print('eqlib OK')"
```

一个最小的"双均线策略"长这样（先不用全懂，感受一下即可）：

```python
from eqlib import *

def initialize(context):
    g.security = '601390'                 # 存一个全局变量：股票代码
    set_benchmark('000300.XSHG')          # 对比基准：沪深300
    run_daily(market_open, time='every_bar')  # 每天开盘时运行 market_open

def market_open(context):
    hist = attribute_history(g.security, 20, '1d', ['close'])  # 取最近20天收盘价
    if hist['close'].iloc[-1] > hist['close'].mean() * 1.02:   # 现价 > 20日均价×1.02
        order_value(g.security, context.portfolio.available_cash)  # 全仓买入

result = run_strategy(initialize, start_date='2024-01-01',
                      end_date='2024-12-31', securities=['601390'])
```

真正的学习，从 [01-学习规划.md](01-学习规划.md) 开始 👉