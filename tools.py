# -*- coding: utf-8 -*-
"""
智能投研系统 - 自定义工具模块
封装 AkShare 数据抓取工具，供「量化与基本面矿工」Agent 使用。
所有 AkShare 调用均带 try-except，防止抓取失败导致流程中断。
"""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

try:
    import akshare as ak
except ImportError:
    ak = None

from crewai.tools import tool


def _ensure_akshare():
    """检查 akshare 是否可用。"""
    if ak is None:
        raise RuntimeError("未安装 akshare，请执行: pip install akshare")


# ---------- 技术指标计算（基于 K 线） ----------


def _calc_ma(series: pd.Series, window: int) -> pd.Series:
    """计算简单移动平均。"""
    return series.rolling(window=window, min_periods=1).mean()


def _calc_ema(series: pd.Series, span: int) -> pd.Series:
    """计算指数移动平均。"""
    return series.ewm(span=span, adjust=False).mean()


def _calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """计算 MACD：DIF, DEA, MACD 柱。"""
    ema_fast = _calc_ema(close, fast)
    ema_slow = _calc_ema(close, slow)
    dif = ema_fast - ema_slow
    dea = _calc_ema(dif, signal)
    macd_bar = (dif - dea) * 2
    return {"DIF": dif, "DEA": dea, "MACD": macd_bar}


def _calc_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI。"""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _calc_boll(close: pd.Series, window: int = 20, num_std: float = 2.0) -> dict:
    """计算布林带：中轨、上轨、下轨。"""
    mid = close.rolling(window=window, min_periods=1).mean()
    std = close.rolling(window=window, min_periods=1).std().fillna(0)
    upper = mid + num_std * std
    lower = mid - num_std * std
    return {"BOLL_MID": mid, "BOLL_UPPER": upper, "BOLL_LOWER": lower}


# ---------- 工具 1：获取技术面数据 ----------


@tool("获取A股技术面数据")
def get_stock_technical_data(symbol: str) -> str:
    """
    获取指定 A 股代码近半年的日 K 线，并计算 20/60 日均线、MACD、RSI、布林带。
    仅返回客观数据摘要，不做主观评价。
    参数 symbol: 6 位 A 股代码，如 '000001'、'600519'。
    """
    try:
        _ensure_akshare()
    except RuntimeError as e:
        return str(e)
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        df = ak.stock_zh_a_hist(
            symbol=symbol.strip(),
            period="daily",
            start_date=start_str,
            end_date=end_str,
            adjust="qfq",
        )
    except Exception as e:
        return f"[技术面数据抓取失败] 股票代码: {symbol}, 错误: {type(e).__name__}: {e}"

    if df is None or df.empty:
        return f"[技术面数据为空] 股票代码: {symbol}，请检查代码或日期范围。"

    # 列名可能为中文
    close_col = "收盘"
    if close_col not in df.columns:
        return f"[技术面数据格式异常] 未找到列 '{close_col}'，当前列: {list(df.columns)}"

    df = df.sort_values("日期").reset_index(drop=True)
    close = df[close_col].astype(float)

    # 计算指标
    ma20 = _calc_ma(close, 20)
    ma60 = _calc_ma(close, 60)
    macd = _calc_macd(close)
    rsi = _calc_rsi(close)
    boll = _calc_boll(close)

    # 取最近一行有效值
    last = df.index[-1]
    latest = {
        "日期": str(df.loc[last, "日期"]),
        "收盘": round(close.iloc[-1], 2),
        "MA20": round(ma20.iloc[-1], 2) if not pd.isna(ma20.iloc[-1]) else None,
        "MA60": round(ma60.iloc[-1], 2) if not pd.isna(ma60.iloc[-1]) else None,
        "MACD_DIF": round(macd["DIF"].iloc[-1], 4) if not pd.isna(macd["DIF"].iloc[-1]) else None,
        "MACD_DEA": round(macd["DEA"].iloc[-1], 4) if not pd.isna(macd["DEA"].iloc[-1]) else None,
        "MACD_bar": round(macd["MACD"].iloc[-1], 4) if not pd.isna(macd["MACD"].iloc[-1]) else None,
        "RSI": round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None,
        "BOLL_上轨": round(boll["BOLL_UPPER"].iloc[-1], 2) if not pd.isna(boll["BOLL_UPPER"].iloc[-1]) else None,
        "BOLL_中轨": round(boll["BOLL_MID"].iloc[-1], 2) if not pd.isna(boll["BOLL_MID"].iloc[-1]) else None,
        "BOLL_下轨": round(boll["BOLL_LOWER"].iloc[-1], 2) if not pd.isna(boll["BOLL_LOWER"].iloc[-1]) else None,
    }

    lines = [
        f"股票代码: {symbol} | 区间: 近半年 | 复权: 前复权",
        f"最新交易日: {latest['日期']}",
        f"收盘价: {latest['收盘']} | MA20: {latest['MA20']} | MA60: {latest['MA60']}",
        f"MACD: DIF={latest['MACD_DIF']}, DEA={latest['MACD_DEA']}, 柱={latest['MACD_bar']}",
        f"RSI(14): {latest['RSI']}",
        f"布林带: 上轨={latest['BOLL_上轨']}, 中轨={latest['BOLL_中轨']}, 下轨={latest['BOLL_下轨']}",
    ]
    return "\n".join(lines)


# ---------- 工具 2：获取基本面/财务数据 ----------


@tool("获取A股基本面与财务数据")
def get_stock_financial_data(symbol: str) -> str:
    """
    获取指定 A 股的核心财务数据：最新市盈率 PE-TTM、营收增长率、现金流状况。
    仅返回客观数据摘要，不做主观评价。
    参数 symbol: 6 位 A 股代码，如 '000001'、'600519'。
    """
    try:
        _ensure_akshare()
    except RuntimeError as e:
        return str(e)
    code = symbol.strip()

    # 1) PE-TTM：优先用乐咕乐股接口
    pe_ttm = None
    try:
        lg_df = ak.stock_a_lg_indicator(stock=code)
        if lg_df is not None and not lg_df.empty:
            # 取最新一行
            last_row = lg_df.iloc[-1]
            if "pe_ttm" in last_row.index:
                pe_ttm = last_row["pe_ttm"]
            elif "pe" in last_row.index:
                pe_ttm = last_row["pe"]
    except Exception as e:
        pe_ttm = f"获取失败({type(e).__name__})"

    # 2) 财务摘要：营收、现金流等（新浪关键指标）
    revenue_growth = None
    cash_flow_info = None
    try:
        abstract_df = ak.stock_financial_abstract(symbol=code)
        if abstract_df is not None and not abstract_df.empty:
            # 列结构: 选项, 指标, 以及各报告期列（如 20231231）
            cols = [c for c in abstract_df.columns if c not in ("选项", "指标")]
            if cols:
                # 找营业总收入
                rev_row = abstract_df[abstract_df["指标"].astype(str).str.contains("营业总收入", na=False)]
                if not rev_row.empty:
                    vals = rev_row[cols].iloc[0].dropna()
                    if len(vals) >= 2:
                        v_new = float(vals.iloc[0])
                        v_old = float(vals.iloc[1])
                        if v_old and v_old != 0:
                            revenue_growth = round((v_new - v_old) / abs(v_old) * 100, 2)
                    elif len(vals) == 1:
                        revenue_growth = "仅一期数据"

                # 现金流：经营现金流净额或每股现金流
                for name in ["经营现金流净额", "经营活动产生的现金流量净额", "每股现金流"]:
                    cf_row = abstract_df[abstract_df["指标"].astype(str).str.contains(name, na=False)]
                    if not cf_row.empty and cols:
                        cf_vals = cf_row[cols].iloc[0].dropna()
                        if not cf_vals.empty:
                            cash_flow_info = f"{name}: 最近期={cf_vals.iloc[0]}"
                            break
    except Exception as e:
        revenue_growth = revenue_growth or f"获取失败({type(e).__name__})"
        cash_flow_info = cash_flow_info or f"获取失败({type(e).__name__})"

    # 若 PE 未从 lg 取到，尝试从新浪摘要取
    if pe_ttm is None:
        try:
            abstract_df = ak.stock_financial_abstract(symbol=code)
            if abstract_df is not None and not abstract_df.empty:
                pe_row = abstract_df[abstract_df["指标"].astype(str).str.contains("市盈率", na=False)]
                if not pe_row.empty:
                    first_col = [c for c in abstract_df.columns if c not in ("选项", "指标")][:1]
                    if first_col:
                        pe_ttm = pe_row[first_col[0]].iloc[0]
        except Exception:
            pass
    if pe_ttm is None:
        pe_ttm = "未获取到"

    lines = [
        f"股票代码: {code}",
        f"市盈率(PE-TTM): {pe_ttm}",
        f"营收增长率(同比/环比): {revenue_growth}",
        f"现金流状况: {cash_flow_info or '未解析到'}",
    ]
    return "\n".join(lines)


# ---------- 导出工具列表（供 agents 使用） ----------


def get_quant_fundamental_tools():
    """返回「量化与基本面矿工」Agent 使用的工具列表。"""
    return [get_stock_technical_data, get_stock_financial_data]


# ---------- 工具 3：网络搜索（供宏观研究员使用） ----------


@tool("DuckDuckGo 网络搜索")
def duckduckgo_search(query: str) -> str:
    """
    使用 DuckDuckGo 在互联网上搜索信息。用于检索宏观政策、行业动态、公司新闻等。
    参数 query: 搜索关键词，建议使用中文或中英混合。
    """
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return f"[搜索无结果] query: {query}"
        lines = [f"- {r.get('title', '')}: {r.get('body', '')[:200]}..." for r in results]
        return "\n".join(lines)
    except Exception as e:
        return f"[搜索失败] query: {query}, 错误: {type(e).__name__}: {e}"


def get_duckduckgo_search_tools():
    """
    返回 DuckDuckGo 搜索工具列表，供「宏观政策与逻辑研究员」使用。
    使用本模块的 @tool 封装，与 CrewAI 兼容；若未安装 duckduckgo-search 则返回空列表。
    """
    try:
        from duckduckgo_search import DDGS  # noqa: F401

        return [duckduckgo_search]
    except ImportError:
        return []
