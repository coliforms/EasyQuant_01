# =====================================================================
# 这个文件是 eqlib（EasyQuant 库）的"总入口"。
# 小白理解：你写策略时只要 `from eqlib import *`，就能直接用下面导入的所有函数。
# 下面那一大串 from ... import ... 就是在"进货"——把库里各种工具搬出来，
# 好让你能用简短的名字（如 order、attribute_history）直接调用它们。
# =====================================================================
"""eqlib — EasyQuant-like API library for local quantitative backtesting.

Data source: akshare
Usage:
    from eqlib import *

    def initialize(context):
        g.security = '601390'
        set_benchmark('000300.XSHG')
        set_option('use_real_price', True)
        run_daily(market_open, time='every_bar')

    def market_open(context):
        close_data = attribute_history(g.security, 5, '1d', ['close'])
        MA5 = close_data['close'].mean()
        current_price = close_data['close'][-1]

        if current_price > 1.01 * MA5:
            order_value(g.security, context.portfolio.available_cash)
            log.info("Buying %s" % g.security)
        elif current_price < MA5 and context.portfolio.positions.get(g.security):
            order_target(g.security, 0)
            log.info("Selling %s" % g.security)

        record(price=current_price, cash=context.portfolio.available_cash)

    # Run backtest
    result = run_backtest(initialize,
                          start_date='2024-01-01',
                          end_date='2025-01-01',
                          starting_cash=100000)
"""

# ─── API 稳定性图例（小白版说明）──────────────────────────────────────────
# 作者用 [STABLE] [EXPERIMENTAL] [DEPRECATED] 给每个函数贴标签，告诉你"能不能放心用"：
#
# STABLE（稳定）      ：名字和用法基本不会变，放心学、放心用，最适合新手。
# EXPERIMENTAL（实验）：随时可能改，别拿来做正式东西，先了解即可。
# DEPRECATED（弃用）  ：以后会被删掉，调用时会弹警告，建议换用新函数。
#
# 小白建议：优先关注标着 [STABLE] 的函数，它们才是常用、靠谱的核心功能。
# ─────────────────────────────────────────────────────────────────────────────

# ── 策略生命周期（[STABLE] 稳定）────────────────────────
# 这些函数控制"策略什么时候跑、按什么节奏跑"：
from eqlib.engine import (
    run_backtest,      # 运行回测：把策略在历史行情上"演一遍"，看赚不赚钱
    run_daily,         # 每天执行某个函数（比如每天开盘时买卖）
    run_weekly,        # 每周执行一次
    run_monthly,       # 每月执行一次
    run_selection,     # 定期执行"选股"函数
    set_handle_data,   # 指定"每根K线都调用"的处理函数
    record,            # 记录自定义指标，方便画图看（如记录现金、价格）
    run_paper_trade,   # 模拟盘（纸面交易）：用最新行情练习，不真花钱
)

# ── 配置（[STABLE] 稳定）──────────────────────────────────
# 这些函数用来"设置回测的规则和参数"：
from eqlib.engine import set_benchmark, set_option, set_order_cost, set_slippage
#   set_benchmark ：设置基准（用来对比的指数，如沪深300）
#   set_option    ：设置选项（如是否用真实价格）
#   set_order_cost：设置手续费/佣金
#   set_slippage  ：设置滑点（想买价和实际成交价的差距）
from eqlib.objects import OrderCost
#   OrderCost     ：手续费参数对象（打包成一份"成本单"）

# ── 通知（[STABLE] 稳定）──────────────────────────────────
# 让程序在出现买卖信号时"提醒你"（比如发消息）：
from eqlib.engine import set_notification_webhook, enable_notification
from eqlib.notification import notify_signal

# ── 滑点模型（[STABLE] 稳定）──────────────────────────────
# 不同方式模拟"实际成交价与预期价的差距"：
from eqlib.slippage import SlippageModel, FixedSlippage, VolumeSlippage
#   SlippageModel  ：滑点模型基类
#   FixedSlippage  ：固定滑点（每次固定差几分钱）
#   VolumeSlippage ：按成交量算滑点

# ── 会话管理（[EXPERIMENTAL] 实验，高级/并发用，新手可跳过）─
from eqlib._state import BacktestSession, get_session
#   用于同时跑多个回测时，各自独立、互不干扰。

# ── 交易下单（[STABLE] 稳定）──────────────────────────────
# 这些是"下单"函数，决定买/卖多少：
from eqlib.trade import (
    order,              # 按"股数"下单（如买100股）
    order_target,       # 下单到"目标股数"（多退少补）
    order_value,        # 按"金额"下单（如买1万元）
    order_target_value, # 下单到"目标金额"
    cancel_order,       # 撤单
    order_lots,         # 按"手"下单（A股1手=100股）
    order_pct,          # 按"仓位百分比"下单（如用30%资金买）
)

# ── 数据获取（[STABLE] 稳定，核心功能）────────────────────
# 这些函数用来"拿股票数据"，是策略的"食材来源"：
from eqlib.data import (
    get_price, history, attribute_history, get_all_securities,
    #   get_price          ：取某只股票某天的价格
    #   history            ：取一段历史行情
    #   attribute_history  ：取某只股票过去N天的数据（算均线常用它）
    #   get_all_securities ：拿所有股票/证券的列表
    download_stock_data, load_csv,
    #   download_stock_data：从网上下载股票数据
    #   load_csv           ：从本地CSV文件读数据
    scan_market, check_golden_cross,
    #   scan_market        ：扫描市场（找符合条件的股票）
    #   check_golden_cross ：检查是否"金叉"（快线上穿慢线，买入信号）
    fetch_stock_data, clear_cache,
    # Financial data  [EXPERIMENTAL]  财务数据（实验）
    get_financial_abstract, get_financial_screen,
    # Index / industry / concept  [STABLE]  指数/行业/概念
    get_index_stocks, get_industry_list, get_industry_stocks,
    get_concept_list, get_concept_stocks, get_industry,
    # Minute-level data  [EXPERIMENTAL]  分钟级数据（实验）
    fetch_minute_data, get_price_minute,
    # Tick data  [EXPERIMENTAL]  逐笔成交数据（实验）
    get_tick_data,
    # Market snapshot, security info, trading calendar  [STABLE]
    # 市场快照 / 股票信息 / 交易日历
    get_current_data, get_security_info, get_trade_days,
    # Fundamentals, money flow, valuation, extras  [EXPERIMENTAL]
    # 基本面 / 资金流 / 估值 / 额外数据（实验）
    get_money_flow, get_billboard_list,
    get_valuation, get_index_weights, get_extras,
    # Universe management  [STABLE]  股票池管理
    set_universe, get_universe,
    # Lifecycle callbacks  [STABLE]  生命周期回调（开盘前/收盘后钩子）
    before_trading_start, after_trading_end,
    # A-share market specific data  [EXPERIMENTAL]  A股特有数据（实验）
    get_north_money_flow,   # 北向资金流向（外资买A股的动向）
    get_margin_data,        # 融资融券数据（借钱炒股数据）
    get_limit_up_down_stats,# 涨跌停统计
    get_restriction_release,# 限售解禁（禁售股解禁上市）
)

# ── 日志（[STABLE] 稳定）──────────────────────────────────
from eqlib.logger import log
#   log ：打印日志（如 log.info("买入") 这样用）

# ── 全局对象 g（[STABLE] 稳定，非常常用）─────────────────
# 下面这段在讲一个"黑科技"：让多个回测同时跑时，各自的 g 互不串线。
# 小白只需记住一句：g 是一个"共享的记事本"，你在策略里用 g.security=xxx
# 存东西，其他函数里就能用 g.security 读回来。
from eqlib.objects import GlobalObject
import eqlib._state as _st

# 备用全局对象：还没开始回测时先用它顶着。
_g_fallback = GlobalObject()


class _GProxy:
    """g 的"传话人"（代理）。

    小白理解：你写的 `g.security = '601390'` 看起来是直接读写一个变量，
    实际上是通过这个"传话人"，把读写转给"当前正在跑的那个回测"的 g。
    这样即使同时跑好几个回测，各自的 g 也不会互相污染。
    名字前面带下划线 `_` 表示"内部使用，你一般不用直接碰它"。
    """

    __slots__ = ()

    @property
    def __class__(self):
        return GlobalObject

    def _target(self):
        """Return the underlying GlobalObject to delegate to.

        Handles the case where run_backtest stores the proxy itself in
        session._g (via ``session._g = eqlib.g``).  In that case we must
        fall back to _g_fallback to avoid infinite recursion.
        """
        sess = _st.get_session()
        g_obj = sess._g
        if g_obj is None or g_obj is self:
            return _g_fallback
        return g_obj

    @property
    def __dict__(self):
        return self._target().__dict__

    def __getattr__(self, name: str):
        return getattr(self._target(), name)

    def __setattr__(self, name: str, value):
        if name in ("__slots__",):
            object.__setattr__(self, name, value)
            return
        setattr(self._target(), name, value)

    def __delattr__(self, name: str):
        delattr(self._target(), name)

    def __contains__(self, name: str) -> bool:
        return hasattr(self._target(), name)

    def __dir__(self):
        return dir(self._target())

    def keys(self):
        return self._target().__dict__.keys()

    def items(self):
        return self._target().__dict__.items()

    def __repr__(self):
        return repr(self._target())


# 全局只有一个 g 实例：你 `import eqlib` 后用的 eqlib.g 就是它。
g = _GProxy()

# ── 上下文对象（[STABLE] 稳定）───────────────────────────
# 回测运行时自动创建，供你在策略里读账户信息：
from eqlib.context import Context, Portfolio, Position
#   Context   ：整个策略的"大环境"，含账户、行情等
#   Portfolio ：你的"投资组合"（持仓+现金，如 context.portfolio.available_cash）
#   Position  ：单只股票的"持仓"（买了多少股、成本多少）

# ── 报告生成（[STABLE] 稳定）─────────────────────────────
# 回测结束后，把结果画成图、写成报告：
from eqlib.report import generate_chart, generate_report_md, generate_report_json, generate_html_report

# ── 引擎内部（[EXPERIMENTAL] 实验，内部使用，新手跳过）───
from eqlib import engine

# ── 数据缓存（[STABLE] 稳定）─────────────────────────────
# 把下载过的数据存到磁盘/内存里，下次直接用，不用重复下载：
from eqlib.data_cache import (
    set_cache_dir, fetch_cached, estimate_memory_mb,
    # Local CSV data store  [STABLE]  本地CSV数据存储
    set_local_data_dir, save_stock_local, load_stock_local,
    has_local_data, list_local_stocks, remove_local_data,
    clear_all_local_data,
)

# ── 组合优化（[EXPERIMENTAL] 实验）───────────────────────
# 帮你在多只股票间分配资金（如最小波动、最大夏普、风险平价）：
from eqlib.optimizer import (
    portfolio_optimizer,
    Bound, MinVariance, MaxSharpe, RiskParity,
)

# ── 绩效归因（[STABLE] 稳定）─────────────────────────────
# 回测结束后分析"到底赚/亏在哪"，以及给策略打分、找瓶颈：
from eqlib.attribution import (
    analyze_returns,        # 计算收益率、回撤、夏普等核心指标
    brinson_attribution,    # 布林森归因：拆解收益来源
    simple_factor_analysis, # 简单因子分析
    fama_french_analysis,   # DEPRECATED（弃用）— 请用 simple_factor_analysis
    grade_strategy,         # 给策略打分
    diagnose_bottleneck,    # 诊断策略瓶颈
    recommend_params,       # 推荐参数
)

# ── 选股（[STABLE] 稳定）─────────────────────────────────
# 从几千只股票里"挑出"符合条件的那批（选股器 + 过滤器）：
from eqlib.selection import (
    StockSelector,        # 选股器基类
    TopNSelector,         # 挑前N名
    MultiFactorSelector,  # 多因子选股
    filter_st_stocks,     # 过滤掉ST股（业绩差、有退市风险的股）
    filter_paused_stocks, # 过滤掉停牌股（暂停交易的股）
    filter_low_price_stocks, # 过滤低价股
    filter_high_pe_stocks,   # 过滤高市盈率股
    fetch_factor_data,    # 取因子数据
)

# ── 股票查询API（[EXPERIMENTAL] 实验，链式筛选）───────────
from eqlib.stock_query import (
    query, valuation, get_fundamentals, get_current_data_object,
)

# ── 机器学习（[EXPERIMENTAL] 实验）───────────────────────
from eqlib.ml import (
    FeaturePipeline, BaseMLModel, MLSelector,
    optimize_hyperparams, auto_tune_selector,
    validate_ml_strategy, check_feature_drift,
)

# ── 工具函数（[STABLE] 稳定）─────────────────────────────
# 指标计算、统计、资金管理等工具箱：
from eqlib import utils

# ── 组合回测（[STABLE] 稳定）─────────────────────────────
from eqlib.portfolio import StrategyConfig, run_portfolio_backtest

# ── 滚动前推分析（[EXPERIMENTAL] 实验）──────────────────
from eqlib.wfa import walk_forward, WFAResult

# ── 科学验证层（[EXPERIMENTAL] 实验）────────────────────
# 作为子模块导入 — 用 ``from eqlib.scientific import validate_backtest``
# 或 ``import eqlib.scientific`` 来访问完整API。
from eqlib.validation_config import ValidationConfig

# ── 组合风控监控（[EXPERIMENTAL] 实验）──────────────────
from eqlib.portfolio_risk import (
    PortfolioRiskMonitor,
    RiskThresholds,
    RiskReport,
    AlertLevel,
    check_kill_switch,
)

# PTrade/QMT adapter — imported as a submodule to avoid shadowing backtest functions:
#   from eqlib.ptrade_adapter import *
# See doc/ptrade_adapter.md for usage instructions.

# Strategy templates (optional import)  [STABLE]
from eqlib import strategies

# ── 公开API清单（__all__）────────────────────────────────
# `from eqlib import *` 时，实际导出的就是下面这份名单。
# 小白不用逐行记，需要时回来查"有没有这个函数"即可。
__all__ = [
    # Lifecycle
    "run_backtest", "run_daily", "run_weekly", "run_monthly", "run_selection",
    "set_handle_data", "record", "run_paper_trade",
    # Config
    "set_benchmark", "set_option", "set_order_cost", "set_slippage", "OrderCost",
    # Notifications
    "set_notification_webhook", "enable_notification", "notify_signal",
    # Slippage models
    "SlippageModel", "FixedSlippage", "VolumeSlippage",
    # Session management
    "BacktestSession", "get_session",
    # Trading
    "order", "order_target", "order_value", "order_target_value", "cancel_order",
    "order_lots", "order_pct",
    # Data
    "get_price", "history", "attribute_history", "get_all_securities",
    "download_stock_data", "load_csv",
    "scan_market", "check_golden_cross",
    "fetch_stock_data", "clear_cache",
    # Financial data
    "get_financial_abstract", "get_financial_screen",
    # Index / industry / concept
    "get_index_stocks", "get_industry_list", "get_industry_stocks",
    "get_concept_list", "get_concept_stocks", "get_industry",
    # Minute-level data
    "fetch_minute_data", "get_price_minute",
    # Tick data
    "get_tick_data",
    # P0: Market snapshot, security info, trading calendar
    "get_current_data", "get_security_info", "get_trade_days",
    # P1: Fundamentals, money flow, valuation, extras
    "get_fundamentals", "get_money_flow", "get_billboard_list",
    "get_valuation", "get_index_weights", "get_extras",
    # Universe management
    "set_universe", "get_universe",
    # P0: Lifecycle callbacks
    "before_trading_start", "after_trading_end",
    # A-share market specific data
    "get_north_money_flow", "get_margin_data",
    "get_limit_up_down_stats", "get_restriction_release",
    # Logging
    "log",
    # Objects
    "g", "GlobalObject", "Context", "Portfolio", "Position",
    # Reporting
    "generate_chart", "generate_report_md", "generate_report_json", "generate_html_report",
    "run_strategy",
    # Engine internals
    "engine",
    # Portfolio optimization
    "portfolio_optimizer", "Bound", "MinVariance", "MaxSharpe", "RiskParity",
    # Attribution analysis
    "analyze_returns", "brinson_attribution",
    "simple_factor_analysis",
    "fama_french_analysis",  # deprecated — use simple_factor_analysis
    "grade_strategy", "diagnose_bottleneck", "recommend_params",
    # Stock selection
    "StockSelector", "TopNSelector", "MultiFactorSelector",
    "filter_st_stocks", "filter_paused_stocks",
    "filter_low_price_stocks", "filter_high_pe_stocks",
    "fetch_factor_data",
    # Data cache
    "set_cache_dir", "fetch_cached", "estimate_memory_mb",
    # Local CSV data store
    "set_local_data_dir", "save_stock_local", "load_stock_local",
    "has_local_data", "list_local_stocks", "remove_local_data",
    "clear_all_local_data",
    # Machine Learning
    "FeaturePipeline",
    "BaseMLModel",
    "MLSelector",
    "optimize_hyperparams",
    "auto_tune_selector",
    "validate_ml_strategy",
    "check_feature_drift",
    # Utilities
    "utils",
    # Portfolio backtest
    "StrategyConfig", "run_portfolio_backtest",
    # Walk-forward analysis
    "walk_forward", "WFAResult",
    # Stock query API
    "query", "valuation", "get_current_data_object",
    # Scientific validation config
    "ValidationConfig",
    # Portfolio risk monitoring
    "PortfolioRiskMonitor", "RiskThresholds", "RiskReport", "AlertLevel",
    "check_kill_switch",
]


# ── 一键回测函数 run_strategy ─────────────────────────────
# 这是最高层的"懒人函数"：给定策略和日期，帮你跑完回测并生成全部报告。
# 小白用法：run_strategy(initialize, start_date='2024-01-01', end_date='2025-01-01')
def run_strategy(initialize_func, start_date=None, end_date=None,
                  starting_cash=100000.0, benchmark="000300.XSHG",
                  handle_data=None, securities=None,
                  report_dir="reports", use_local: bool = False,
                  max_memory_mb: int = 1024,
                  selection_func=None, selection_rebalance: str = "monthly:1"):
    """
    High-level strategy runner. Runs backtest and generates all reports.

    Parameters:
        initialize_func: user's initialize(context)
        start_date: 'YYYY-MM-DD' or datetime.date
        end_date: 'YYYY-MM-DD' or datetime.date
        starting_cash: initial capital
        benchmark: benchmark code
        handle_data: optional handle_data(context, data) function
        securities: list of stock codes to preload. Passing all stocks
            you'll trade significantly speeds up large backtests.
        report_dir: directory for output reports
        use_local: if True, load data from local CSV files first.
                   Downloads and saves to local CSV if not found.
                   Subsequent runs will use the saved local data.
        max_memory_mb: memory limit in MB for in-memory dict caches.
                       Default 1024 (1 GB). Results are identical
                       regardless of whether dict caches are used.
        selection_func: optional callable taking (context) and returning
            a list of selected security codes.  Runs periodically on
            rebalance days to update context.universe.
        selection_rebalance: when to run selection_func.  Format:
            - "monthly:N" — Nth day of month (1-31), default "monthly:1"
            - "weekly:N" — Nth weekday (0=Mon, 4=Fri), default "weekly:0"
            - "daily" — every trading day

    Returns:
        Backtest result dict
    """
    import datetime as _dt
    import os as _os

    if start_date is None:
        start_date = _dt.date.today() - _dt.timedelta(days=365)
    if isinstance(start_date, str):
        start_date = _dt.datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date is None:
        end_date = _dt.date.today()
    if isinstance(end_date, str):
        end_date = _dt.datetime.strptime(end_date, "%Y-%m-%d").date()

    # B2: handle_data is now passed directly to run_backtest (not set on old session)

    # 真正跑回测：把 handle_data 传给新会话，引擎开始按交易日模拟交易
    result = run_backtest(
        initialize_func, start_date, end_date,
        starting_cash=starting_cash, benchmark=benchmark,
        securities=securities, use_local=use_local,
        max_memory_mb=max_memory_mb,
        selection_func=selection_func,
        selection_rebalance=selection_rebalance,
        handle_data=handle_data,
    )

    if result is None:
        print("Backtest failed: no result returned.")
        return None

    # ── 生成报告 ─────────────────────────────────────────
    # 建好报告输出文件夹，并用当前时间生成文件名（避免覆盖旧报告）
    _os.makedirs(report_dir, exist_ok=True)
    timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    chart_path = f"{report_dir}/backtest_{timestamp}.png"
    report_html_path = f"{report_dir}/backtest_{timestamp}.html"
    report_md_path = f"{report_dir}/backtest_{timestamp}.md"
    report_json_path = f"{report_dir}/backtest_{timestamp}.json"

    generate_chart(result, chart_path)          # 画收益曲线图
    generate_html_report(result, report_html_path)  # 生成网页版报告
    generate_report_md(result, report_md_path)      # 生成Markdown报告
    generate_report_json(result, report_json_path)  # 生成JSON数据文件

    # 计算最终收益：账户总价值 - 初始资金
    ctx = result["context"]
    pnl = ctx.portfolio.total_value - ctx.portfolio.starting_cash
    pnl_pct = (pnl / ctx.portfolio.starting_cash) * 100

    # 在终端打印关键结果
    print(f"\nFinal value: {ctx.portfolio.total_value:,.2f}")
    print(f"P&L: {pnl:,.2f} ({pnl_pct:+.2f}%)")
    print(f"Trades: {len(result['trade_log'])}")
    print(f"\nChart:  {chart_path}")
    print(f"HTML:   {report_html_path}")
    print(f"Report: {report_md_path}")
    print(f"Data:   {report_json_path}")

    return result


# ── 支撑/阻力风险预算研究策略（[EXPERIMENTAL] 实验）────
from eqlib.strategies.sr_risk_budget import SRRiskConfig, make_sr_risk_budget_strategy

__all__ += ["SRRiskConfig", "make_sr_risk_budget_strategy"]