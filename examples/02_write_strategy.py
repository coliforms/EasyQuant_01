"""
02 - Writing Your First Strategy
===============================

Demonstrates the core pattern for writing an EasyQuant strategy:
- initialize(context): one-time setup (benchmark, costs, scheduling)
- market_open(context): daily trading logic (data -> signal -> order)
- g object: global state shared across callbacks
- run_daily(): schedule functions to run each trading day

This example implements a dual Moving Average crossover strategy
on a single stock, which is the "Hello World" of quantitative trading.

Teaching Objectives:
    - Strategy lifecycle: initialize -> daily callback
    - The g object for global strategy state
    - attribute_history() for fetching historical data
    - order_value() and order_target() for placing trades
    - record() for charting custom metrics

Expected Output:
    - Strategy initialization messages
    - Buy/sell signals logged during backtest
    - Evaluation panel with Sharpe ratio, max drawdown, etc.

Run:
    python examples/02_write_strategy.py
"""
# =====================================================================
# 小白导读：这个文件教你写"第一个策略"——双均线金叉/死叉策略。
# 整个流程只有 3 步：
#   1. initialize()  开机设置（只跑一次）：设基准、设手续费、存参数、安排每天跑 market_open
#   2. market_open() 每天执行（每个交易日跑）：取历史数据 → 算均线 → 判断金叉/死叉 → 下单
#   3. 底部 if __name__ 块：真正"发动"回测，跑完生成报告
# =====================================================================
import sys                       # 系统工具（用来改 import 搜索路径）
from pathlib import Path         # 处理文件路径

# 允许当脚本直接运行：python examples/NN_xxx.py
# 把项目根目录塞进 sys.path，这样下面的 from eqlib import ... 才找得到 eqlib
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)   # 算出项目根目录（往上两楼）
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import os                        # 文件/文件夹操作（后面建 reports 目录用）

# ── 从 eqlib 前台进货：本策略要用到的工具 ─────────────────────
from eqlib import (
    run_strategy,          # 懒人函数：一键跑完整回测并出报告
    set_benchmark,         # 设基准（用来对比"跑赢没跑赢大盘"）
    set_order_cost,        # 设手续费/印花税
    set_slippage,          # 设滑点（想买价和实际成交价的差）
    run_daily,             # 安排"每个交易日执行某函数"
    attribute_history,     # 取过去 N 天的历史数据（算均线的核心）
    order_value,           # 按"金额"下单买入
    order_target,          # 按"目标持仓数"下单（清仓 = target 设为 0）
    record,                # 记录数据，回测结束后画图用
    log,                   # 打印日志
    g,                     # 全局"记事本"，跨函数存变量
)
# ── 从 examples 的公共配置进货：股票池、日期、费率等默认值 ─────
from examples._defaults import (
    STOCKS, STOCKS_TRADE, INDEX_HS300,                     # 股票代码表 / 交易代码表 / 沪深300指数
    DEFAULT_ORDER_COST, DEFAULT_SLIPPAGE, INITIAL_CASH,    # 默认手续费 / 默认滑点 / 初始资金
    START_DATE, END_DATE, verify_data_available, print_evaluation,  # 起止日期 / 检查数据 / 打印评估
)


# ============================================================
# 策略参数（你可以改这里，体验不同结果）
# ============================================================

# 为什么用 5 和 20？5日均线反映"短期趋势"，20日均线反映"中期趋势"，
# 这是业界最常用的默认组合，用来捕捉"约2周"的动量反转。
SECURITY = STOCKS["bank"]              # 601398 工商银行（股票代码）
SECURITY_TRADE = STOCKS_TRADE["bank"]  # 601398.XSHG（带交易所后缀，下单用）
FAST_PERIOD = 5                        # 快线周期：5日均线
SLOW_PERIOD = 20                       # 慢线周期：20日均线


# ============================================================
# Strategy code
# ============================================================

def initialize(context):
    """One-time strategy setup.

    Called once at the start of the backtest. Use this to:
    - Set the benchmark for performance comparison
    - Configure trading costs
    - Store strategy parameters on the g (global) object
    - Schedule trading functions via run_daily/run_weekly/run_monthly
    """
    # 大白话：这个函数只在回测"开头"跑一次，负责"开机设置"。

    # ① 设基准：沪深300指数，用来对比"你的策略跑赢大盘没有"
    set_benchmark(INDEX_HS300)

    # ② 设交易成本：手续费 + 滑点（都用项目默认值）
    set_order_cost(DEFAULT_ORDER_COST)
    set_slippage(DEFAULT_SLIPPAGE)

    # ③ 把参数存进 g（全局记事本）
    #    g 在整个回测期间一直存在，任何函数都能读它
    g.security = SECURITY
    g.security_trade = SECURITY_TRADE
    g.fast_period = FAST_PERIOD
    g.slow_period = SLOW_PERIOD

    # ④ 定义股票池（本策略交易哪些股票）——这里就一只
    context.universe = [g.security]

    # ⑤ 安排 market_open 函数"每个交易日"都跑一次
    run_daily(market_open, time="every_bar")

    # ⑥ 打印一条启动日志
    log.info("Strategy initialized: MA %d/%d on %s",
             g.fast_period, g.slow_period, g.security)


def market_open(context):
    """Daily trading logic: dual MA crossover.

    Called once per trading day. The workflow is:
    1. Fetch historical data via attribute_history()
    2. Calculate signals (MA crossover)
    3. Execute trades via order_value() or order_target()
    4. Record metrics for charting

    Signal logic:
    - BUY  when fast MA crosses above slow MA (golden cross)
    - SELL when fast MA crosses below slow MA (death cross)
    """
    # 大白话：这个函数"每个交易日"跑一次，是本策略的核心。
    # 流程：取数据 → 算均线 → 判断金叉/死叉 → 下单 → 记录画图

    security = g.security
    security_trade = g.security_trade

    # 第1步：取足够多的历史数据（慢线20天 + 富余5天 = 25根K线）
    bars_needed = g.slow_period + 5
    hist = attribute_history(security, bars_needed, "1d", ["close"])
    # 数据不够就算不了均线，直接"今天不操作"退出
    if hist is None or hist.empty or len(hist) < g.slow_period:
        return

    close = hist["close"]                    # 只取"收盘价"这一列
    current_price = close.iloc[-1]           # 最新一天的收盘价（iloc[-1] = 倒数第一行）

    # 第2步：计算快慢两条均线
    fast_ma = close.rolling(g.fast_period).mean()   # 5日均线
    slow_ma = close.rolling(g.slow_period).mean()   # 20日均线

    # 前面几天还不够算均线（值是 NaN 空值），数据不足就退出
    if len(fast_ma.dropna()) < 2 or len(slow_ma.dropna()) < 2:
        return

    # 比较"今天 vs 昨天"来判断均线是否发生了"交叉"
    prev_fast, curr_fast = fast_ma.iloc[-2], fast_ma.iloc[-1]   # 昨天快线、今天快线
    prev_slow, curr_slow = slow_ma.iloc[-2], slow_ma.iloc[-1]   # 昨天慢线、今天慢线

    # 金叉：昨天快线还在慢线下方，今天快线穿到慢线上方 → 买入信号
    golden_cross = (prev_fast <= prev_slow) and (curr_fast > curr_slow)
    # 死叉：昨天快线还在慢线上方，今天快线跌到慢线下方 → 卖出信号
    death_cross = (prev_fast >= prev_slow) and (curr_fast < curr_slow)

    # 第3步：下单
    # 判断"现在有没有持仓"（amount > 0 表示手里有股票）
    has_position = (security_trade in context.portfolio.positions
                    and context.portfolio.positions[security_trade].amount > 0)

    if golden_cross and not has_position:
        # 金叉 且 没持仓 → 买入：拿 95% 可用现金去买（留 5% 当手续费缓冲）
        cash = context.portfolio.available_cash
        if cash > current_price * 100:       # 至少够买 100 股（1手）才买
            order_value(security_trade, cash * 0.95)
            log.info("BUY (golden cross): %s @ %.2f, fast=%.2f > slow=%.2f",
                     security, current_price, curr_fast, curr_slow)

    elif death_cross and has_position:
        # 死叉 且 有持仓 → 清仓卖出（order_target 目标持仓 = 0 就是全卖）
        order_target(security_trade, 0)
        log.info("SELL (death cross): %s @ %.2f, fast=%.2f < slow=%.2f",
                 security, current_price, curr_fast, curr_slow)

    # 第4步：记录数据，回测结束后画图看曲线
    record(
        price=current_price,                        # 当前价
        fast_ma=curr_fast,                          # 快线值
        slow_ma=curr_slow,                          # 慢线值
        total_value=context.portfolio.total_value,  # 账户总资产
    )


# ============================================================
# Run backtest
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("02 - Writing Your First Strategy (MA Crossover)")
    print("=" * 55)

    # Verify data is available before running
    actual_start, actual_end = verify_data_available(
        SECURITY, START_DATE, END_DATE)

    os.makedirs("reports", exist_ok=True)

    result = run_strategy(
        initialize_func=initialize,
        start_date=actual_start,
        end_date=actual_end,
        starting_cash=INITIAL_CASH,
        benchmark=INDEX_HS300,
        securities=[SECURITY],
        report_dir="reports",
        use_local=True,
    )

    if result:
        print_evaluation(result, "MA Crossover (5/20)")