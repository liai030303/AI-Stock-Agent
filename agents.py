# -*- coding: utf-8 -*-
"""
智能投研系统 - 核心智能体定义
按照设计文档定义三个 Agent：量化与基本面矿工、宏观政策研究员、首席投资总监。
支持 OpenAI 兼容接口的国内大模型：智谱(Zhipu)、DeepSeek、通义千问(Qwen)。
"""

import os

from langchain_openai import ChatOpenAI
from crewai import Agent

from tools import get_quant_fundamental_tools, get_duckduckgo_search_tools


# ---------- 厂商配置（OpenAI 兼容接口）----------
LLM_PROVIDER_CONFIG = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "api_key_env": "QWEN_API_KEY",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-4-flash",
        "api_key_env": "ZHIPU_API_KEY",
    },
}


def get_llm(
    provider: str = "zhipu",
    model: str | None = None,
    temperature: float = 0.2,
):
    """
    返回配置好的 ChatOpenAI 实例（OpenAI 兼容接口）。
    provider: "zhipu" | "deepseek" | "qwen"，默认 "zhipu"。
    model: 可选覆盖默认模型。
    """
    if provider not in LLM_PROVIDER_CONFIG:
        raise ValueError(
            f"不支持的 provider: {provider}，可选: deepseek, qwen, zhipu"
        )
    config = LLM_PROVIDER_CONFIG[provider]
    api_key_env = config["api_key_env"]
    try:
        api_key = os.environ.get(api_key_env)
        if not api_key or not api_key.strip():
            env_hint = {
                "DEEPSEEK_API_KEY": "请先设置 DEEPSEEK_API_KEY 环境变量",
                "QWEN_API_KEY": "请先设置 QWEN_API_KEY 环境变量",
                "ZHIPU_API_KEY": "请先设置 ZHIPU_API_KEY 环境变量",
            }
            raise ValueError(env_hint.get(api_key_env, f"请先设置 {api_key_env} 环境变量"))
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"读取 {api_key_env} 时出错: {e}") from e

    return ChatOpenAI(
        base_url=config["base_url"],
        api_key=api_key,
        model=model or config["model"],
        temperature=temperature,
    )


# ---------- Agent 1: 量化与基本面矿工 ----------

QUANT_MINER_ROLE = "量化与基本面矿工"
QUANT_MINER_GOAL = (
    "从公开数据源准确提取目标股票的量化技术数据与核心财务数据，"
    "输出纯粹、无主观评价的客观数据面板。"
)
QUANT_MINER_BACKSTORY = """你是一名绝对理性的数据提取专家，专注于 A 股标的的量化与基本面数据。
你只负责调用工具获取：近半年日 K 线衍生的技术指标（20/60 日均线、MACD、RSI、布林带），
以及核心财务数据（最新市盈率 PE-TTM、营收增长率、现金流状况）。
你不做任何主观解读或投资建议，只整理并呈现原始数据与简要统计。"""


def create_quant_fundamental_miner_agent(
    llm=None,
    provider: str = "zhipu",
    verbose: bool = True,
) -> Agent:
    """创建「量化与基本面矿工」Agent。"""
    return Agent(
        role=QUANT_MINER_ROLE,
        goal=QUANT_MINER_GOAL,
        backstory=QUANT_MINER_BACKSTORY,
        llm=llm or get_llm(provider=provider),
        tools=get_quant_fundamental_tools(),
        verbose=verbose,
        allow_delegation=False,
        max_iter=3,
    )


# ---------- Agent 2: 宏观政策与逻辑研究员 ----------

MACRO_ANALYST_ROLE = "宏观政策与逻辑研究员"
MACRO_ANALYST_GOAL = (
    "基于网络信息，研判目标公司所处行业的宏观政策与业务逻辑，"
    "输出政策面是顺风还是逆风的逻辑推理报告。"
)
MACRO_ANALYST_BACKSTORY = """你是一名洞察国家大势与产业逻辑的分析师，擅长从宏观政策与行业动态中提炼投资逻辑。
你的职责是：搜索目标公司所在行业的最新国家宏观政策、目标公司近期核心业务动态，
并判断该公司实际业务与当前宏观风口（如出海、新质生产力、设备更新等）的契合度。
你只输出逻辑推理与事实依据，明确给出政策面是顺风还是逆风的结论，不做最终买卖决策。"""


def create_macro_policy_analyst_agent(
    llm=None,
    provider: str = "zhipu",
    verbose: bool = True,
) -> Agent:
    """创建「宏观政策与逻辑研究员」Agent，使用 DuckDuckGo 搜索工具。"""
    return Agent(
        role=MACRO_ANALYST_ROLE,
        goal=MACRO_ANALYST_GOAL,
        backstory=MACRO_ANALYST_BACKSTORY,
        llm=llm or get_llm(provider=provider),
        tools=get_duckduckgo_search_tools(),
        verbose=verbose,
        allow_delegation=False,
        max_iter=6,
    )


# ---------- Agent 3: 首席投资总监 CIO ----------

CIO_ROLE = "首席投资总监"
CIO_GOAL = (
    "整合量化数据与宏观逻辑，践行「贵极反贱、贱极反贵」的投资哲学，"
    "输出结构化的最终战报与操作指令。"
)
CIO_BACKSTORY = """你是践行「贵上极则反贱，贱下极则反贵。贵出如粪土，贱取如珠玉」的终极决策者。
你依据前序报告中的估值、技术指标、宏观政策与基本面，做出最终交易决策。
你的决策逻辑包括：极度冰点（PE 极低 + RSI 超卖 + 宏观顺风 + 基本面健康）可触发买入；
极度泡沫（PE 畸高 + RSI 超买 + 市场情绪狂热）则提示减仓；若宏观研究员指出标的纯属蹭概念、业务与政策背离，则一票否决买入。
你只输出结构化战报：估值与周期定性、宏观共振分析、铁血操作指令，不依赖外部工具。"""


def create_cio_agent(
    llm=None,
    provider: str = "zhipu",
    verbose: bool = True,
) -> Agent:
    """创建「首席投资总监」Agent。无工具，纯推理。"""
    return Agent(
        role=CIO_ROLE,
        goal=CIO_GOAL,
        backstory=CIO_BACKSTORY,
        llm=llm or get_llm(provider=provider),
        tools=[],
        verbose=verbose,
        allow_delegation=False,
        max_iter=2,
    )


# ---------- 工厂函数：一次创建全部 Agent ----------


def create_all_agents(
    llm=None,
    provider: str = "zhipu",
    verbose: bool = True,
) -> list[Agent]:
    """按顺序返回：量化矿工、宏观研究员、CIO。provider 会透传给 get_llm()。"""
    _llm = llm or get_llm(provider=provider)
    return [
        create_quant_fundamental_miner_agent(llm=_llm, provider=provider, verbose=verbose),
        create_macro_policy_analyst_agent(llm=_llm, provider=provider, verbose=verbose),
        create_cio_agent(llm=_llm, provider=provider, verbose=verbose),
    ]
