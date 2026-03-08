# -*- coding: utf-8 -*-
"""
AI 智能投研系统 - Streamlit 交互式 Web 前端
用户输入股票代码或名称，展示 CIO 终极战报。
"""

import streamlit as st

from main import run_research


st.set_page_config(
    page_title="AI 智能投研委员会",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("📈 AI 智能投研系统")
st.markdown(
    "输入目标股票代码或公司名称，由 **量化矿工**、**宏观研究员** 与 **首席投资总监** 协同研判，"
    "输出基于「贵出如粪土、贱取如珠玉」理念的终极战报。"
)
with st.sidebar:
    st.caption("模型与配置")
    provider = st.selectbox(
        "LLM 厂商",
        options=["zhipu", "qwen", "deepseek"],
        index=0,
        help="需在 .env 中配置对应 API Key（如 ZHIPU_API_KEY、QWEN_API_KEY）",
    )

st.divider()

stock_input = st.text_input(
    "目标股票代码或名称",
    value="",
    placeholder="例如：600519 或 贵州茅台",
    key="stock_symbol",
)

col1, col2, _ = st.columns([1, 1, 4])
with col1:
    run_button = st.button("🚀 开始深度研判", type="primary", use_container_width=True)

if run_button:
    symbol = (stock_input or "").strip()
    if not symbol:
        st.warning("请先输入股票代码或名称（如 600519）。")
        st.stop()

    with st.spinner(
        "特工们正在后台疯狂查阅数据和宏观政策，请耐心等待（约 1-2 分钟）..."
    ):
        try:
            report = run_research(stock_symbol=symbol, provider=provider)
            st.divider()
            st.subheader("📋 首席投资总监 · 终极战报")
            st.markdown(report)
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"研判过程中发生错误：{e}")
