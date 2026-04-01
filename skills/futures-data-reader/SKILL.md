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
- 现货价格与基差分析
- 期货库存数据
- 手续费与保证金查询
- 展期收益率分析

## 关于 AkShare

**AkShare** 是 Python 开源金融数据接口库，提供股票、期货、期权、基金、债券、外汇等金融数据。

- **GitHub**: https://github.com/akfamily/akshare
- **文档**: https://akshare.akfamily.xyz/
- **安装**: `pip install akshare pandas numpy`

### ⚠️ Windows 特别注意事项

1. **Python版本**: 建议使用 Python 3.11
   ```bash
   py -0  # 查看可用版本
   ```

2. **运行方式**: 使用 `py -3.11` 启动器
   ```bash
   py -3.11 your_script.py
   ```

3. **安装依赖**:
   ```bash
   py -3.11 -m pip install akshare pandas numpy
   ```

## 支持的期货品种

### 广州期货交易所 (GFEX)

| 主力连续代码 | 品种名称 | 上市日期 | 备注 |
|-------------|----------|----------|------|
| lc0 | 碳酸锂主连 | 2023-07-21 | 主力品种 |
| si0 | 工业硅主连 | 2022-12-22 | |
| ps0 | 多晶硅主连 | 2024-12-26 | |

### 上海期货交易所 (SHFE)

| 主力连续代码 | 品种名称 | 主力连续代码 | 品种名称 |
|-------------|----------|-------------|----------|
| cu0 | 铜主连 | rb0 | 螺纹钢主连 |
| al0 | 铝主连 | hc0 | 热卷主连 |
| zn0 | 锌主连 | bu0 | 沥青主连 |
| pb0 | 铅主连 | fu0 | 燃料油主连 |
| ni0 | 镍主连 | ru0 | 橡胶主连 |
| au0 | 黄金主连 | ag0 | 白银主连 |
| sn0 | 锡主连 | ss0 | 不锈钢主连 |
| sp0 | 纸浆主连 | wr0 | 线材主连 |

### 大连商品交易所 (DCE)

| 主力连续代码 | 品种名称 | 主力连续代码 | 品种名称 |
|-------------|----------|-------------|----------|
| i0 | 铁矿石主连 | m0 | 豆粕主连 |
| j0 | 焦炭主连 | y0 | 豆油主连 |
| jm | 焦煤主连 | p0 | 棕榈油主连 |
| a0 | 豆一主连 | b0 | 豆二主连 |
| c0 | 玉米主连 | cs0 | 玉米淀粉主连 |
| l0 | 聚乙烯主连 | v0 | PVC主连 |
| pp0 | 聚丙烯主连 | eg0 | 乙二醇主连 |
| jd0 | 鸡蛋主连 | lh0 | 生猪主连 |

### 郑州商品交易所 (CZCE)

| 主力连续代码 | 品种名称 | 主力连续代码 | 品种名称 |
|-------------|----------|-------------|----------|
| sr0 | 白糖主连 | ta0 | PTA主连 |
| cf0 | 棉花主连 | ma0 | 甲醇主连 |
| zc0 | 动力煤主连 | fg0 | 玻璃主连 |
| rm0 | 菜粕主连 | oi0 | 菜油主连 |
| rs0 | 菜籽主连 | ap0 | 苹果主连 |
| ur0 | 尿素主连 | sa0 | 纯碱主连 |

### 中国金融期货交易所 (CFFEX)

| 主力连续代码 | 品种名称 | 主力连续代码 | 品种名称 |
|-------------|----------|-------------|----------|
| if0 | 沪深300股指主连 | ih0 | 上证50股指主连 |
| ic0 | 中证500股指主连 | im0 | 中证1000股指主连 |
| ts0 | 2年期国债主连 | tf0 | 5年期国债主连 |
| t0 | 10年期国债主连 | tl0 | 30年期国债主连 |

## 使用方法

### 1. 获取历史K线数据

```python
import akshare as ak

# 获取期货日K线数据
df = ak.futures_zh_daily_sina(symbol="lc0")
print(df.tail())
```

返回列: `date`, `open`, `high`, `low`, `close`, `volume`, `hold`, `settle`

### 2. 获取实时行情

```python
import akshare as ak

# 获取最新行情
df = ak.futures_zh_daily_sina(symbol="lc0")
latest = df.iloc[-1]
print(f"最新价: {latest['close']}")
```

### 3. 计算技术指标

```python
import akshare as ak
import pandas as pd
import numpy as np

def calculate_indicators(df):
    """计算技术指标"""
    close = df['close']
    
    # MA
    df['ma5'] = close.rolling(5).mean()
    df['ma10'] = close.rolling(10).mean()
    df['ma20'] = close.rolling(20).mean()
    
    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    df['dif'] = ema12 - ema26
    df['dea'] = df['dif'].ewm(span=9).mean()
    df['macd'] = (df['dif'] - df['dea']) * 2
    
    # KDJ
    low_n = df['low'].rolling(9).min()
    high_n = df['high'].rolling(9).max()
    rsv = (close - low_n) / (high_n - low_n) * 100
    df['k'] = rsv.ewm(com=2).mean()
    df['d'] = df['k'].ewm(com=2).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']
    
    # 布林带
    df['boll_mid'] = close.rolling(20).mean()
    std = close.rolling(20).std()
    df['boll_upper'] = df['boll_mid'] + 2 * std
    df['boll_lower'] = df['boll_mid'] - 2 * std
    
    return df

df = ak.futures_zh_daily_sina(symbol="lc0")
df = calculate_indicators(df)
print(df[['date', 'close', 'ma20', 'macd']].tail())
```

### 4. 获取期货手续费与保证金

```python
import akshare as ak

# 获取所有期货手续费信息
df = ak.futures_comm_info(symbol="所有")
print(df.head())

# 获取广期所手续费
df = ak.futures_comm_info(symbol="广州期货交易所")
print(df)
```

### 5. 获取库存数据

```python
import akshare as ak

# 东方财富库存数据
df = ak.futures_inventory_em(symbol="碳酸锂")
print(df.tail())

# 99期货网库存数据
df = ak.futures_inventory_99(symbol="lc")
print(df.tail())
```

### 6. 获取基差数据

```python
import akshare as ak

# 近期基差
df = ak.futures_spot_price("20240430")
print(df)

# 历史基差
df = ak.futures_spot_price_previous("20240430")
print(df)
```

### 7. 获取展期收益率

```python
import akshare as ak

# 某品种历史展期收益率
df = ak.get_roll_yield_bar(type_method="date", var="LC", 
                            start_day="20240101", end_day="20240430")
print(df)

# 某日所有品种展期收益率
df = ak.get_roll_yield_bar(type_method="var", date="20240430")
print(df)
```

### 8. 获取交易日历

```python
import akshare as ak

# 获取某交易日所有合约规则
df = ak.futures_rule(date="20240430")
print(df)
```

### 9. 获取所有期货品种交易时间

```python
import akshare as ak

# 期货交易时间表
df = ak.futures_display_sina()
print(df)
```

## 数据来源

- **AkShare** - 金融数据开源库
- **新浪期货** - 日K线数据
- **东方财富** - 实时行情、库存数据
- **九期网** - 手续费数据
- **99期货网** - 库存数据

## 技术指标说明

| 指标 | 说明 |
|------|------|
| ma5, ma10, ma20, ma60 | 5/10/20/60日移动平均线 |
| macd, dif, dea | MACD指标 |
| k, d, j | KDJ指标 |
| boll_upper, boll_mid, boll_lower | 布林带 |
| rsi | RSI相对强弱指标 |

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
| hold | 持仓量 |
| settle | 结算价 |

## 期货基础概念

### 主力连续合约
- 代码以 `0` 结尾（如 lc0, si0）
- 由不同时期主力合约拼接而成

### 指数连续合约
- 代码以 `99` 结尾（如 lc99）
- 所有合约加权平均

### 展期收益率
- 近月合约与远月合约的价差比率
- Contango: 远月升水，展期收益为负
- Backwardation: 远月贴水，展期收益为正

## 注意事项

1. 部分期货品种可能无数据，请确认品种代码正确
2. 数据获取可能受网络限制，请确保网络通畅
3. 历史数据可能不完整，以实际返回为准
4. 实时行情有时间延迟，仅供参考
5. 主力连续合约代码使用小写（如 lc0 而非 LC0）

## 故障排查

### ModuleNotFoundError: No module named 'akshare'
```bash
# 确认安装
pip show akshare

# 使用 py 启动器安装
py -3.11 -m pip install akshare

# 检查 Python 版本
py -0
```

### 数据返回为空或0
- 检查品种代码是否正确（小写：lc0 而非 LC0）
- 新品种可能尚未上线
- 打印原始数据检查：`print(df.tail())`

### 列名不匹配
- AkShare返回列名可能为英文或中文
- 代码需同时兼容：`date`/`日期`, `close`/`收盘` 等

### 网络超时
- 检查网络连接
- 尝试增加超时时间
- 可能是数据源维护期间

## 扩展阅读

- AkShare 官方文档: https://akshare.akfamily.xyz/
- GitHub: https://github.com/akfamily/akshare
- 期货交易所官网:
  - 广州期货交易所: http://www.gfex.com.cn
  - 上期所: https://www.shfe.com.cn
  - 大商所: http://www.dce.com.cn
  - 郑商所: http://www.czce.com.cn
  - 中金所: http://www.cffex.com.cn
