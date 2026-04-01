# -*- coding: utf-8 -*-
"""
期货数据获取模块
依赖: pip install akshare pandas numpy
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# 期货品种映射
FUTURES_MAP = {
    "lc0": {"name": "碳酸锂", "exchange": "广州期货交易所", "symbol": "lc0"},
    "cu0": {"name": "铜", "exchange": "上期所", "symbol": "cu0"},
    "al0": {"name": "铝", "exchange": "上期所", "symbol": "al0"},
    "zn0": {"name": "锌", "exchange": "上期所", "symbol": "zn0"},
    "pb0": {"name": "铅", "exchange": "上期所", "symbol": "pb0"},
    "ni0": {"name": "镍", "exchange": "上期所", "symbol": "ni0"},
    "au0": {"name": "黄金", "exchange": "上期所", "symbol": "au0"},
    "ag0": {"name": "白银", "exchange": "上期所", "symbol": "ag0"},
    "ru0": {"name": "橡胶", "exchange": "上期所", "symbol": "ru0"},
    "rb0": {"name": "螺纹钢", "exchange": "上期所", "symbol": "rb0"},
    "hc0": {"name": "热卷", "exchange": "上期所", "symbol": "hc0"},
    "i0": {"name": "铁矿石", "exchange": "大商所", "symbol": "i0"},
    "j0": {"name": "焦炭", "exchange": "大商所", "symbol": "j0"},
    "jm": {"name": "焦煤", "exchange": "大商所", "symbol": "jm"},
    "m0": {"name": "豆粕", "exchange": "大商所", "symbol": "m0"},
    "y0": {"name": "豆油", "exchange": "大商所", "symbol": "y0"},
    "p0": {"name": "棕榈油", "exchange": "大商所", "symbol": "p0"},
    "sr0": {"name": "白糖", "exchange": "郑商所", "symbol": "sr0"},
    "cf0": {"name": "棉花", "exchange": "郑商所", "symbol": "cf0"},
    "zc0": {"name": "动力煤", "exchange": "郑商所", "symbol": "zc0"},
    "ta0": {"name": "PTA", "exchange": "郑商所", "symbol": "ta0"},
    "ma0": {"name": "甲醇", "exchange": "郑商所", "symbol": "ma0"},
}


def get_futures_daily(futures_code: str = "lc0", days: int = 365) -> pd.DataFrame:
    """获取期货日K线数据"""
    try:
        df = ak.futures_zh_daily_sina(symbol=futures_code)
        
        if '日期' in df.columns:
            df = df.rename(columns={'日期': 'date'})
        if '开盘' in df.columns:
            df = df.rename(columns={'开盘': 'open'})
        if '最高' in df.columns:
            df = df.rename(columns={'最高': 'high'})
        if '最低' in df.columns:
            df = df.rename(columns={'最低': 'low'})
        if '收盘' in df.columns:
            df = df.rename(columns={'收盘': 'close'})
        if '成交量' in df.columns:
            df = df.rename(columns={'成交量': 'volume'})
        if '成交额' in df.columns:
            df = df.rename(columns={'成交额': 'amount'})
        if '持仓量' in df.columns:
            df = df.rename(columns={'持仓量': 'oi'})
            
        if 'date' in df.columns:
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
                'open': latest.get('开盘', 0),
                'high': latest.get('最高', 0),
                'low': latest.get('最低', 0),
                'close': latest.get('收盘', 0),
                'volume': latest.get('成交量', 0),
                'chg': latest.get('涨跌', 0),
                'pct_chg': latest.get('涨跌幅', 0),
            }
    except Exception as e:
        print(f"获取实时行情失败: {e}")
    return {}


def get_spot_price(commodity: str = "碳酸锂") -> dict:
    """获取现货价格"""
    try:
        df = ak.futures_spot_price_daily()
        for _, row in df.iterrows():
            if commodity in str(row.get('品类', '')):
                return {
                    'name': row.get('品类', ''),
                    'price': row.get('均价', 0),
                    'date': str(row.get('日期', '')),
                }
    except Exception as e:
        print(f"获取现货价格失败: {e}")
    return {}


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算技术指标"""
    if df.empty or 'close' not in df.columns:
        return df
        
    close = df['close']
    
    # 移动平均线
    df['ma5'] = close.rolling(window=5).mean()
    df['ma10'] = close.rolling(window=10).mean()
    df['ma20'] = close.rolling(window=20).mean()
    df['ma60'] = close.rolling(window=60).mean()
    
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['dif'] = ema12 - ema26
    df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
    df['macd'] = (df['dif'] - df['dea']) * 2
    
    # KDJ
    low_n = df['low'].rolling(window=9).min()
    high_n = df['high'].rolling(window=9).max()
    rsv = (close - low_n) / (high_n - low_n) * 100
    df['k'] = rsv.ewm(com=2, adjust=False).mean()
    df['d'] = df['k'].ewm(com=2, adjust=False).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']
    
    # 布林带
    df['boll_mid'] = close.rolling(window=20).mean()
    std = close.rolling(window=20).std()
    df['boll_upper'] = df['boll_mid'] + 2 * std
    df['boll_lower'] = df['boll_mid'] - 2 * std
    
    # RSI
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
    
    pct_30d = 0
    if len(df) >= 30:
        pct_30d = (close - df.iloc[-30]['close']) / df.iloc[-30]['close'] * 100
        
    pct_90d = 0
    if len(df) >= 90:
        pct_90d = (close - df.iloc[-90]['close']) / df.iloc[-90]['close'] * 100
        
    return {
        'date': str(latest.get('date', '')),
        'close': close,
        'high': latest.get('high', 0),
        'low': latest.get('low', 0),
        'volume': latest.get('volume', 0),
        'pct_30d': round(pct_30d, 2),
        'pct_90d': round(pct_90d, 2),
    }


if __name__ == "__main__":
    print("测试获取碳酸锂期货数据...")
    df = get_futures_daily("lc0", days=30)
    print(df)
    
    print("\n计算技术指标...")
    df = calculate_indicators(df)
    print(df[['date', 'close', 'ma5', 'ma20', 'macd']].tail())
    
    print("\n行情摘要...")
    summary = get_summary(df)
    print(summary)