# =====================================================================
# 这个文件教你"取股票数据"——量化四步曲（取数据→看数据→分析→写策略）的第一步。
# 它演示 5 种取数方法，每种包在一个 demo 函数里，底部 main 依次跑一遍。
# =====================================================================
"""
01 - Data Fetching
==================

Demonstrates the core data APIs for retrieving A-share market data.
This is typically the first step in any quantitative workflow:
get data -> explore -> analyze -> build strategy.

Teaching Objectives:
    - get_price(): historical OHLCV for a single stock
    - fetch_stock_data(): raw data interface with multi-source fallback
    - get_all_securities(): full A-share stock listing
    - download_stock_data() + load_csv(): local CSV workflow
    - scan_market(): real-time market screening

Expected Output:
    - Printed DataFrames showing stock data
    - CSV file saved to data/ directory
    - Market scan results (may be empty outside trading hours)

Run:
    python examples/01_fetch_data.py
"""
import sys                      # 系统相关（这里用来改 import 搜索路径）
from pathlib import Path        # 处理文件路径

# 让本脚本能"从任意目录"直接运行：把项目根目录塞进 sys.path，
# 这样下面的 from eqlib import ... 才不会报"找不到模块"。
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)   # 算出项目根目录
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import os                       # 操作系统相关（这里用来建文件夹）
from datetime import datetime, timedelta   # 处理日期（今天、往前推多少天）

# 从 eqlib 前台"进货"，拿 6 个取数工具 + 1 个日志工具：
from eqlib import (
    get_price,             # 取单只股票的历史K线（最常用）
    fetch_stock_data,      # 取数据，自动换数据源（东财/腾讯/新浪…谁快用谁）
    get_all_securities,    # 拿全市场所有股票的名单
    download_stock_data,   # 下载数据存成本地CSV
    load_csv,              # 从本地CSV读回数据
    scan_market,           # 实时扫盘选股
    log,                   # 打印日志
)
# STOCKS 是一个"股票字典"：给你起好记的别名（如 "liquor"→茅台代码 600519）
from examples._defaults import STOCKS


def demo_get_price():
    """演示1：取单只股票的历史 OHLCV 数据（开高低收量）。

    get_price() 是最常用的取数函数，返回一个 pandas 的 DataFrame 表格，
    列有：open(开)、high(高)、low(低)、close(收)、volume(量)。
    """
    security = STOCKS["liquor"]  # 600519 贵州茅台（"liquor"=白酒）
    # 日期范围：今天往前推120天 ~ 往前推30天（约3个月，避开最近30天）
    end = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")

    print("--- get_price ---")
    # 取数据：df 就是一张"日期 × 开高低收量"的表格
    df = get_price(security, start_date=start, end_date=end)
    if df is not None and not df.empty:      # 拿到数据且不为空
        print(f"  {security}: {len(df)} bars from {start} to {end}")   # 一共几根K线
        print(f"  Latest close: {df['close'].iloc[-1]:.2f}")  # 最新收盘价（取close列最后一行）
        print(f"  Columns: {df.columns.tolist()}")            # 有哪些列
        print(df.tail(3).to_string())                          # 打印最后3行
    else:
        print(f"  No data for {security}")                     # 没拿到数据
    print()


def demo_fetch_stock_data():
    """演示2：原始取数接口，带"多数据源自动兜底"。

    fetch_stock_data() 会依次尝试多个数据源（东方财富、腾讯、新浪、
    宝Stock），谁先成功就用谁的结果。默认用"qfq(前复权)"调整价格。
    """
    security = STOCKS["bank"]  # 601398 工商银行（"bank"=银行）
    end = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    print("--- fetch_stock_data ---")
    df = fetch_stock_data(security, start, end)   # 注意：这里用"位置传参"，不像上面用 start_date=
    if df is not None and not df.empty:
        print(f"  {security}: {len(df)} bars (qfq adjusted)")
        print(df.tail(3).to_string())
    else:
        print(f"  No data for {security}")
    print()


def demo_get_all_securities():
    """演示3：拿全市场 A 股名单。

    返回一张表格，列有：code(代码)、name(名字)。
    想遍历全市场找股票时用它。
    """
    print("--- get_all_securities ---")
    df = get_all_securities()      # 一口气拿全市场所有股票
    if df is not None and not df.empty:
        print(f"  Total A-share stocks: {len(df)}")   # 一共多少只股票
        print(df.head(5).to_string())                 # 打印前5行
    print()


def demo_download_and_load():
    """演示4：把数据下载存成 CSV，再读回来。

    好处：离线也能分析，或者反复用同一份数据时不用每次都联网。
    """
    security = STOCKS["ev"]  # 002594 比亚迪（"ev"=新能源车）
    end = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

    print("--- download_stock_data + load_csv ---")
    os.makedirs("data", exist_ok=True)   # 建一个 data 文件夹（已存在就不报错）
    path = download_stock_data(security, start, end, output_dir="data")  # 下载并返回保存路径
    if path:                              # 下载成功（拿到路径）
        print(f"  Saved to: {path}")
        df = load_csv(path)               # 从CSV读回成表格
        if df is not None and not df.empty:
            print(f"  Loaded {len(df)} bars from CSV")
            print(df.head(3).to_string()) # 打印前3行
    else:
        print(f"  Download failed for {security}")   # 下载失败
    print()


def demo_scan_market():
    """演示5：实时扫盘，按条件筛股票。

    scan_market() 扫描全 A 股，按这些条件过滤：
    - min_price / max_price        ：股价范围
    - min_pct_change / max_pct_change：当日涨跌幅范围
    - max_pe                       ：市盈率上限

    注意：结果取决于当前行情。非交易时段可能筛出的股票很少，属正常。
    """
    print("--- scan_market ---")
    candidates = scan_market(
        min_price=20,      # 股价至少20元
        min_pct_change=2,  # 当天至少涨2%
        max_pct_change=5,  # 当天最多涨5%
        max_pe=30,         # 市盈率不超过30倍
    )
    if candidates is not None and not candidates.empty:
        print(f"  Found {len(candidates)} matching stocks")   # 找到几只符合条件的
        print(candidates.head(10).to_string())               # 打印前10只
    else:
        print("  No stocks match the criteria (normal outside trading hours)")
    print()


# 程序入口：只有"直接运行本文件"时才执行下面代码（被别的文件 import 时不执行）
if __name__ == "__main__":
    print("=" * 55)
    print("01 - Data Fetching APIs")
    print("=" * 55)
    print()

    # 依次跑 5 个演示，每个演示一种取数方法
    demo_get_price()             # 1. 取单只股票历史K线
    demo_fetch_stock_data()      # 2. 多数据源兜底取数
    demo_get_all_securities()    # 3. 全市场股票名单
    demo_download_and_load()     # 4. 下载CSV再读回
    demo_scan_market()           # 5. 实时扫盘选股