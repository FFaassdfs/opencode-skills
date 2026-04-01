---
name: futures-data-reader
description: 读取期货行情数据，支持历史K线、实时行情、技术指标计算。使用AkShare获取数据。
---

# 期货数据读取技能

## 概述

本技能提供期货数据读取功能，支持：
- 历史K线数据（日/周/月）
- 实时行情数据
- 技术指标计算（MA、MACD、KDJ、布林带等）
- 现货价格联动分析
- 多期货品种支持

## 何时使用

- 用户需要获取期货价格数据
- 用户需要技术分析指标
- 用户需要生成期货分析报告
- 用户需要期货与现货联动分析

## 支持的期货品种

| 品种代码 | 品种名称 | 交易所 |
|----------|----------|--------|
| lc0 | 碳酸锂主连 | 广州期货交易所 |
| cu0 | 铜主连 | 上期所 |
| al0 | 铝主连 | 上期所 |
| zn0 | 锌主连 | 上期所 |
| pb0 | 铅主连 | 上期所 |
| ni0 | 镍主连 | 上期所 |
| au0 | 黄金主连 | 上期所 |
| ag0 | 白银主连 | 上期所 |
| ru0 | 橡胶主连 | 上期所 |
| rb0 | 螺纹钢主连 | 上期所 |
| hc0 | 热卷主连 | 上期所 |
| i0 | 铁矿石主连 | 大商所 |
| j0 | 焦炭主连 | 大商所 |
| jm | 焦煤主连 | 大商所 |
| m0 | 豆粕主连 | 大商所 |
| y0 | 豆油主连 | 大商所 |
| p0 | 棕榈油主连 | 大商所 |
| sr0 | 白糖主连 | 郑商所 |
| cf0 | 棉花主连 | 郑商所 |
| zc0 | 动力煤主连 | 郑商所 |
| ta0 | PTA主连 | 郑商所 |
| ma0 | 甲醇主连 | 郑商所 |

## 使用方法

### 1. 获取历史K线数据

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from futures_data import get_futures_daily

# 获取碳酸锂期货日K线
df = get_futures_daily("lc0", days=365)
print(df.tail())
```

### 2. 计算技术指标

```python
from futures_data import calculate_indicators

df_with_indicators = calculate_indicators(df)
print(df_with_indicators[['date', 'close', 'ma5', 'ma20', 'macd', 'boll_upper', 'boll_lower']].tail())
```

### 3. 获取实时行情

```python
from futures_data import get_realtime_quote

quote = get_realtime_quote("lc0")
print(f"最新价: {quote['close']}, 涨跌: {quote['pct_chg']}%")
```

### 4. 获取现货价格

```python
from futures_data import get_spot_price

spot = get_spot_price("碳酸锂")
print(f"现货价格: {spot}")
```

## 数据来源

- **AkShare** - 金融数据开源库
- **新浪期货** - 日K线数据
- **东方财富** - 实时行情
- **现货价格** - 卓创/百川等

## 输出格式

数据以 Pandas DataFrame 格式返回，包含以下列：

| 列名 | 说明 |
|------|------|
| date | 交易日期 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| close | 收盘价 |
| volume | 成交量 |
| amount | 成交额 |
| oi | 持仓量 |

## 技术指标说明

| 指标 | 说明 |
|------|------|
| ma5, ma10, ma20, ma60 | 5/10/20/60日移动平均线 |
| macd, dif, dea | MACD指标 |
| k, d, j | KDJ指标 |
| boll_upper, boll_mid, boll_lower | 布林带 |

## 依赖安装

```bash
pip install akshare pandas numpy
```

## 注意事项

1. 部分期货品种可能无数据，请确认品种代码正确
2. 数据获取可能受网络限制，请确保网络通畅
3. 历史数据可能不完整，以实际返回为准
4. 实时行情有时间延迟，仅供参考