"""
集团OA数据库连接模块 - 100.67 (ecology)
SQL Server 2008 R2 @ 192.168.100.67
"""

import pyodbc
from contextlib import contextmanager

# 连接配置
OA_DB_CONFIG = {
    "driver": "SQL Server",
    "server": "192.168.100.67",
    "database": "ecology",
    "uid": "ReadOA",
    "pwd": "oa168",
}

_CONN_STR = (
    "DRIVER={{{driver}}};"
    "SERVER={server};"
    "DATABASE={database};"
    "UID={uid};"
    "PWD={pwd};"
).format(**OA_DB_CONFIG)


def get_connection(timeout: int = 10) -> pyodbc.Connection:
    """返回一个 pyodbc 连接对象（调用方负责关闭）"""
    return pyodbc.connect(_CONN_STR, timeout=timeout)


@contextmanager
def oa_conn(timeout: int = 10):
    """
    上下文管理器，自动关闭连接。

    用法:
        with oa_conn() as conn:
            df = pd.read_sql("SELECT TOP 10 * FROM HrmResource", conn)
    """
    conn = pyodbc.connect(_CONN_STR, timeout=timeout)
    try:
        yield conn
    finally:
        conn.close()


def query(sql: str, params=None, timeout: int = 10):
    """
    执行 SQL 并返回 list[dict] 结果。

    用法:
        rows = query("SELECT TOP 5 * FROM HrmResource")
        for row in rows:
            print(row)
    """
    with oa_conn(timeout) as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def query_df(sql: str, params=None, timeout: int = 10):
    """
    执行 SQL 并返回 pandas DataFrame。
    需要已安装 pandas。

    用法:
        df = query_df("SELECT TOP 100 * FROM HrmResource")
    """
    import pandas as pd
    with oa_conn(timeout) as conn:
        if params:
            return pd.read_sql(sql, conn, params=params)
        return pd.read_sql(sql, conn)


def test_connection() -> bool:
    """测试连接是否正常，返回 True/False"""
    try:
        rows = query("SELECT @@VERSION AS ver")
        print("[OK] 连接成功:", rows[0]["ver"][:60], "...")
        return True
    except Exception as e:
        print("[FAIL] 连接失败:", e)
        return False


if __name__ == "__main__":
    test_connection()
