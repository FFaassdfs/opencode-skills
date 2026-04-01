# -*- coding: utf-8 -*-
"""
期货数据获取模块
依赖: pip install akshare pandas numpy

Windows使用:
    py -3.11 -m pip install akshare pandas numpy
    py -3.11 your_script.py

参考文档: https://akshare.akfamily.xyz/
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


FUTURES_MAP = {
    # 广州期货交易所 (GFEX)
    "lc0": {"name": "碳酸锂", "exchange": "广州期货交易所", "symbol": "lc"},
    "si0": {"name": "工业硅", "exchange": "广州期货交易所", "symbol": "si"},
    "ps0": {"name": "多晶硅", "exchange": "广州期货交易所", "symbol": "ps"},
    # 上海期货交易所 (SHFE)
    "cu0": {"name": "铜", "exchange": "上期所", "symbol": "cu"},
    "al0": {"name": "铝", "exchange": "上期所", "symbol": "al"},
    "zn0": {"name": "锌", "exchange": "上期所", "symbol": "zn"},
    "pb0": {"name": "铅", "exchange": "上期所", "symbol": "pb"},
    "ni0": {"name": "镍", "exchange": "上期所", "symbol": "ni"},
    "au0": {"name": "黄金", "exchange": "上期所", "symbol": "au"},
    "ag0": {"name": "白银", "exchange": "上期所", "symbol": "ag"},
    "ru0": {"name": "橡胶", "exchange": "上期所", "symbol": "ru"},
    "rb0": {"name": "螺纹钢", "exchange": "上期所", "symbol": "rb"},
    "hc0": {"name": "热卷", "exchange": "上期所", "symbol": "hc"},
    "bu0": {"name": "沥青", "exchange": "上期所", "symbol": "bu"},
    "fu0": {"name": "燃料油", "exchange": "上期所", "symbol": "fu"},
    "sn0": {"name": "锡", "exchange": "上期所", "symbol": "sn"},
    "ss0": {"name": "不锈钢", "exchange": "上期所", "symbol": "ss"},
    "sp0": {"name": "纸浆", "exchange": "上期所", "symbol": "sp"},
    # 大连商品交易所 (DCE)
    "i0": {"name": "铁矿石", "exchange": "大商所", "symbol": "i"},
    "j0": {"name": "焦炭", "exchange": "大商所", "symbol": "j"},
    "jm": {"name": "焦煤", "exchange": "大商所", "symbol": "jm"},
    "m0": {"name": "豆粕", "exchange": "大商所", "symbol": "m"},
    "y0": {"name": "豆油", "exchange": "大商所", "symbol": "y"},
    "p0": {"name": "棕榈油", "exchange": "大商所", "symbol": "p"},
    "a0": {"name": "豆一", "exchange": "大商所", "symbol": "a"},
    "b0": {"name": "豆二", "exchange": "大商所", "symbol": "b"},
    "c0": {"name": "玉米", "exchange": "大商所", "symbol": "c"},
    "cs0": {"name": "玉米淀粉", "exchange": "大商所", "symbol": "cs"},
    "l0": {"name": "聚乙烯", "exchange": "大商所", "symbol": "l"},
    "v0": {"name": "PVC", "exchange": "大商所", "symbol": "v"},
    "pp0": {"name": "聚丙烯", "exchange": "大商所", "symbol": "pp"},
    "eg0": {"name": "乙二醇", "exchange": "大商所", "symbol": "eg"},
    "jd0": {"name": "鸡蛋", "exchange": "大商所", "symbol": "jd"},
    "lh0": {"name": "生猪", "exchange": "大商所", "symbol": "lh"},
    # 郑州商品交易所 (CZCE)
    "sr0": {"name": "白糖", "exchange": "郑商所", "symbol": "sr"},
    "cf0": {"name": "棉花", "exchange": "郑商所", "symbol": "cf"},
    "ta0": {"name": "PTA", "exchange": "郑商所", "symbol": "ta"},
    "ma0": {"name": "甲醇", "exchange": "郑商所", "symbol": "ma"},
    "zc0": {"name": "动力煤", "exchange": "郑商所", "symbol": "zc"},
    "fg0": {"name": "玻璃", "exchange": "郑商所", "symbol": "fg"},
    "rm0": {"name": "菜粕", "exchange": "郑商所", "symbol": "rm"},
    "oi0": {"name": "菜油", "exchange": "郑商所", "symbol": "oi"},
    "rs0": {"name": "菜籽", "exchange": "郑商所", "symbol": "rs"},
    "ap0": {"name": "苹果", "exchange": "郑商所", "symbol": "ap"},
    "ur0": {"name": "尿素", "exchange": "郑商所", "symbol": "ur"},
    "sa0": {"name": "纯碱", "exchange": "郑商所", "symbol": "sa"},
    # 中国金融期货交易所 (CFFEX)
    "if0": {"name": "沪深300股指", "exchange": "中金所", "symbol": "if"},
    "ih0": {"name": "上证50股指", "exchange": "中金所", "symbol": "ih"},
    "ic0": {"name": "中证500股指", "exchange": "中金所", "symbol": "ic"},
    "im0": {"name": "中证1000股指", "exchange": "中金所", "symbol": "im"},
    "ts0": {"name": "2年期国债", "exchange": "中金所", "symbol": "ts"},
    "tf0": {"name": "5年期国债", "exchange": "中金所", "symbol": "tf"},
    "t0": {"name": "10年期国债", "exchange": "中金所", "symbol": "t"},
    "tl0": {"name": "30年期国债", "exchange": "中金所", "symbol": "tl"},
}


def get_futures_daily(futures_code: str = "lc0", days: int = 365) -> pd.DataFrame:
    """获取期货日K线数据"""
    try:
        df = ak.futures_zh_daily_sina(symbol=futures_code)
        
        if df.empty:
            return pd.DataFrame()
        
        if '日期' in df.columns:
            df = df.rename(columns={
                '日期': 'date', '开盘': 'open', '最高': 'high',
                '最低': 'low', '收盘': 'close', '成交量': 'volume',
                '成交额': 'amount', '持仓量': 'oi'
            })
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        if days and days > 0:
            df = df.tail(days)
        
        return df.reset_index(drop=True)
        
    except Exception as e:
        print(f"获取期货数据失败: {e}")
        return pd.DataFrame()


def get_realtime_quote(futures_code: str = "lc0") -> dict:
    """获取期货实时行情"""
    try:
        df = ak.futures_zh_daily_sina(symbol=futures_code)
        if not df.empty:
            latest = df.iloc[-1]
            return {
                'name': FUTURES_MAP.get(futures_code, {}).get('name', futures_code),
                'date': str(latest.get('date', latest.get('日期', ''))),
                'open': latest.get('open', latest.get('开盘', 0)),
                'high': latest.get('high', latest.get('最高', 0)),
                'low': latest.get('low', latest.get('最低', 0)),
                'close': latest.get('close', latest.get('收盘', 0)),
                'volume': latest.get('volume', latest.get('成交量', 0)),
                'settle': latest.get('settle', latest.get('结算价', 0)),
            }
    except Exception as e:
        print(f"获取实时行情失败: {e}")
    return {}


def get_comm_info(exchange: str = "所有") -> pd.DataFrame:
    """获取期货手续费与保证金"""
    try:
        return ak.futures_comm_info(symbol=exchange)
    except Exception as e:
        print(f"获取手续费数据失败: {e}")
        return pd.DataFrame()


def get_inventory_em(symbol: str = "lc") -> pd.DataFrame:
    """获取东方财富库存数据"""
    try:
        return ak.futures_inventory_em(symbol=symbol)
    except Exception as e:
        print(f"获取库存数据失败: {e}")
        return pd.DataFrame()


def get_spot_price(date: str = None) -> pd.DataFrame:
    """获取基差数据"""
    try:
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        return ak.futures_spot_price(date=date)
    except Exception as e:
        print(f"获取基差数据失败: {e}")
        return pd.DataFrame()


def get_roll_yield(type_method: str = "var", date: str = None, 
                   var: str = None, **kwargs) -> pd.DataFrame:
    """获取展期收益率"""
    try:
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        return ak.get_roll_yield_bar(
            type_method=type_method, 
            date=date, 
            var=var, 
            **kwargs
        )
    except Exception as e:
        print(f"获取展期收益率失败: {e}")
        return pd.DataFrame()


def get_futures_rule(date: str = None) -> pd.DataFrame:
    """获取交易日历"""
    try:
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        return ak.futures_rule(date=date)
    except Exception as e:
        print(f"获取交易日历失败: {e}")
        return pd.DataFrame()


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算技术指标"""
    if df.empty or 'close' not in df.columns:
        return df
    
    close = df['close']
    
    df['ma5'] = close.rolling(window=5).mean()
    df['ma10'] = close.rolling(window=10).mean()
    df['ma20'] = close.rolling(window=20).mean()
    df['ma60'] = close.rolling(window=60).mean()
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['dif'] = ema12 - ema26
    df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
    df['macd'] = (df['dif'] - df['dea']) * 2
    
    low_n = df['low'].rolling(window=9).min()
    high_n = df['high'].rolling(window=9).max()
    rsv = (close - low_n) / (high_n - low_n) * 100
    df['k'] = rsv.ewm(com=2, adjust=False).mean()
    df['d'] = df['k'].ewm(com=2, adjust=False).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']
    
    df['boll_mid'] = close.rolling(window=20).mean()
    std = close.rolling(window=20).std()
    df['boll_upper'] = df['boll_mid'] + 2 * std
    df['boll_lower'] = df['boll_mid'] - 2 * std
    
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df


def get_summary(df: pd.DataFrame) -> dict:
    """获取行情摘要"""
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    close = latest.get('close', 0)
    
    pct_5d = 0
    if len(df) >= 5:
        pct_5d = (close - df.iloc[-5]['close']) / df.iloc[-5]['close'] * 100
    
    pct_20d = 0
    if len(df) >= 20:
        pct_20d = (close - df.iloc[-20]['close']) / df.iloc[-20]['close'] * 100
    
    return {
        'date': str(latest.get('date', '')),
        'close': close,
        'open': latest.get('open', 0),
        'high': latest.get('high', 0),
        'low': latest.get('low', 0),
        'volume': latest.get('volume', 0),
        'settle': latest.get('settle', 0),
        'pct_5d': round(pct_5d, 2),
        'pct_20d': round(pct_20d, 2),
    }


if __name__ == "__main__":
    print("=== 期货数据获取测试 ===")
    
    print("\n1. 获取碳酸锂期货数据...")
    df = get_futures_daily("lc0", days=30)
    print(df.tail())
    
    print("\n2. 获取实时行情...")
    quote = get_realtime_quote("lc0")
    print(quote)
    
    print("\n3. 计算技术指标...")
    df = calculate_indicators(df)
    print(df[['date', 'close', 'ma20', 'macd']].tail())
    
    print("\n4. 行情摘要...")
    summary = get_summary(df)
    print(summary)
