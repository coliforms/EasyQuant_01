# pandas / numpy 最小速查（配合 EasyQuant 读代码）

> 用途：这不是教程，是一张「地图」。读项目代码时，遇到下面某个方法，回来查这一行即可。
> 原则：**只学项目里出现的用法，不铺开学 pandas 全家桶。**

---

## 0. 先记住两个「容器」概念（地基）

| 名字 | 一句话 | 类比 |
|------|--------|------|
| **DataFrame** | 一张有行有列的**表格** | 一张 Excel 表 |
| **Series** | 表格里的**一列** | Excel 里的某一列 |

`attribute_history()` / `get_price()` 返回的都是 **DataFrame**。
用 `df['close']` 取一列后，得到的是 **Series**。

---

## 1. 取数据（最高频，必须会）

| 写法 | 含义 | 项目真实例子 |
|------|------|-------------|
| `df['close']` | 取出 `close` 这一列 | `hist['close']` |
| `.iloc[-1]` | 这一列**最后一个**值（最新一天） | `close.iloc[-1]` → 今天收盘价 |
| `.iloc[0]` | 第一个值（最早一天） | `north['date'].iloc[0]` |
| `.iloc[-2]` | 倒数第二个（昨天） | `fast_ma.iloc[-2]` → 昨天的均线 |
| `.tail(N)` | 最后 N 行 | `df.tail(3)`、`volume.tail(5)` |
| `.head(N)` | 前 N 行 | `df.head(5)` |

> 补充：`df['close'][-1]` 和 `df['close'].iloc[-1]` 效果一样，项目里两者都有，认得出即可。

---

## 2. 算指标（必须会）

| 写法 | 含义 | 项目真实例子 |
|------|------|-------------|
| `.mean()` | 求平均值 | `close_data['close'].mean()` → 5 日均值 |
| `.sum()` | 求和 | `north["net_buy"].tail(5).sum()` |
| `.max()` / `.min()` | 最大 / 最小 | `hist["high"].tail(20).max()` |
| `.std()` | 标准差（衡量波动大小） | `daily_rets.std()` |
| `.rolling(N).mean()` | **滚动平均**，即 N 日移动均线 | `close.rolling(20).mean()` → 20 日均线 |

> `.rolling(N)` 是量化里**最重要**的一个：先取一个"滑动的 N 天窗口"，再对窗口算平均/最大/最小等。

---

## 3. 判断与清洗（常见）

| 写法 | 含义 | 项目真实例子 |
|------|------|-------------|
| `.empty` | 判断表格是否**为空** | `if hist is None or hist.empty:` |
| `len(df)` | 表格**行数**（多少根 K 线） | `len(df)` → 拿到多少天数据 |
| `.dropna()` | **去掉**空值（NaN） | `fast_ma.dropna()` |
| `.pct_change()` | 每行相对上一行的**涨跌幅** | `close.pct_change()` → 每日收益率 |
| `.astype(float)` | 把数据转成**浮点数**类型 | `records.total_value.astype(float)` |

> 为什么总出现 `.dropna()`？因为 `rolling(20)` 前 19 天凑不满 20 天，会产生空值，需要去掉再判断。

---

## 4. 进阶（先跳过，遇到再回来查）

| 写法 | 含义 |
|------|------|
| `.cumprod()` | 累计相乘（算净值曲线用） |
| `.cummax()` | 累计最大值（算回撤用） |
| `.loc[start:end]` | 按**标签/日期**切片 |
| `.reset_index(drop=True)` | 重置行号索引 |
| `.reindex(...)` | 对齐索引（让两条线日期一致） |
| `.columns.tolist()` | 取出所有列名 |
| `.to_string()` | 把表格转成文本方便打印 |
| `pd.to_datetime(...)` | 把字符串转成时间 |
| `pd.Timestamp(...)` | 构造一个时间点 |
| `pd.Series([...])` / `pd.concat([...])` | 手工造一列 / 拼接 |

---

## 5. numpy（项目里极少用，知道即可）

| 写法 | 含义 | 项目真实例子 |
|------|------|-------------|
| `np.mean(x)` | 求列表平均值 | `np.mean(momentums)` |
| `np.std(x)` | 求列表标准差 | `np.std(momentums, ddof=1)` |

> numpy 本质是"高效的数字数组"。pandas 底层就用了它，但你读 EasyQuant 代码时几乎只会在「对一组数求均值/标准差」时见到 `np.mean` / `np.std`，其余交给 pandas 就够了。

---

## 6. 对照项目里最典型的一段（读代码神器）

以 `examples/02_write_strategy.py` 的双均线为例，逐行拆解：

```python
hist = attribute_history(security, bars_needed, "1d", ["close"])  # 拿到 DataFrame

close = hist["close"]                       # 取 'close' 这一列 → Series
current_price = close.iloc[-1]              # 最后一个值 → 今天收盘价

fast_ma = close.rolling(5).mean()           # 每 5 天滑动求平均 → 5 日均线
slow_ma = close.rolling(20).mean()          # 每 20 天滑动求平均 → 20 日均线

prev_fast, curr_fast = fast_ma.iloc[-2], fast_ma.iloc[-1]   # 昨天均线、今天均线
golden_cross = (prev_fast <= prev_slow) and (curr_fast > curr_slow)  # 金叉判断
```

看懂这 6 行，你就已经掌握这个项目里 **80%** 的 pandas 用法了。

---

## 7. 学习方法建议

1. 先只看 **第 0、1、2 节**，其余遇到再查。
2. 每读到一个新方法，就回来在对应表格里**打个勾**。
3. 千万别去查 `rolling` 还有什么参数、`iloc` 还能怎么用——**够用即停**。