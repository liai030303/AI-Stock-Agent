# -*- coding: utf-8 -*-
"""
AI 智能投研系统 - 主程序入口
组装 Crew，按顺序执行矿工 → 宏观研究员 → CIO，输出最终战报。
支持国内大模型：智谱(zhipu)、DeepSeek、通义千问(qwen)，均使用 OpenAI 兼容接口。

用法: python main.py [--provider zhipu|deepseek|qwen]
所有 API Key 写入 .env，程序会根据 --provider 自动选用对应的 key。
"""

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()  # 加载 .env 中所有 key（ZHIPU_API_KEY、DEEPSEEK_API_KEY、QWEN_API_KEY 等）

from crewai import Crew, Process

from agents import create_all_agents, LLM_PROVIDER_CONFIG
from tasks import create_all_tasks


# 厂商与所需环境变量映射（.env 中可同时配置多个，运行时按 --provider 选用）
PROVIDER_ENV_KEYS = {
    "zhipu": "ZHIPU_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "QWEN_API_KEY",
}


def run_research(stock_symbol: str, provider: str = "zhipu") -> str:
    """
    执行投研流程：组建 Crew，按顺序执行矿工 → 宏观研究员 → CIO，返回 CIO 的最终战报字符串。
    供 CLI 或 Streamlit 等前端调用。

    :param stock_symbol: 用户输入的目标股票代码或名称（如 600519、贵州茅台）。
    :param provider: LLM 厂商，可选 zhipu / deepseek / qwen，默认 zhipu。
    :return: 首席投资总监的终极战报文本。
    :raises ValueError: provider 不支持或对应 API Key 未配置。
    """
    stock_symbol = (stock_symbol or "").strip()
    if not stock_symbol:
        raise ValueError("请输入有效的股票代码或名称。")

    # ---------- 环境配置与安全校验（从 .env 读取对应 key）----------
    env_key = PROVIDER_ENV_KEYS.get(provider)
    if not env_key:
        raise ValueError(
            f"不支持的 provider: {provider}，可选: zhipu, deepseek, qwen"
        )
    api_key = os.environ.get(env_key)
    if not api_key or not str(api_key).strip():
        raise ValueError(
            f"请先在 .env 中设置 {env_key}！当前使用 provider={provider}，需要对应的 API Key。"
        )

    # CrewAI 内部 OpenAI 提供商会读取 OPENAI_API_KEY / OPENAI_BASE_URL
    provider_config = LLM_PROVIDER_CONFIG.get(provider, {})
    if provider_config:
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = provider_config.get("base_url", "")

    # ---------- 组建 Agents、Tasks 与 Crew ----------
    agents = create_all_agents(provider=provider)
    miner_task, macro_task, cio_task = create_all_tasks(
        agents[0], agents[1], agents[2],
        symbol_or_company_name=stock_symbol,
    )

    crew = Crew(
        agents=agents,
        tasks=[miner_task, macro_task, cio_task],
        process=Process.sequential,
        verbose=True,
        max_rpm=15,
    )

    result = crew.kickoff()
    # 兼容 CrewOutput（.raw）与直接字符串
    output = getattr(result, "raw", result)
    return str(output) if output is not None else ""


def parse_args():
    parser = argparse.ArgumentParser(description="AI 智能投研系统")
    parser.add_argument(
        "-p", "--provider",
        choices=["zhipu", "deepseek", "qwen"],
        default="zhipu",
        help="LLM 厂商，默认 zhipu",
    )
    parser.add_argument(
        "-s", "--symbol",
        default="600519",
        help="目标股票代码或名称，默认 600519",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    selected_provider = args.provider
    target_symbol = args.symbol

    try:
        print(
            "\n🚀 AI 智能投研委员会开始对 [ {} ] 展开深度调研（LLM: {}）...\n".format(
                target_symbol, selected_provider
            )
        )
        report = run_research(stock_symbol=target_symbol, provider=selected_provider)
        print("\n" + "=" * 60)
        print("📋 首席投资总监 · 终极战报")
        print("=" * 60 + "\n")
        print(report)
    except ValueError as e:
        print(f"\n❌ {e}\n", file=sys.stderr)
        sys.exit(1)
