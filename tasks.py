# -*- coding: utf-8 -*-
"""
智能投研系统 - 任务定义
为三个 Agent 分配具体 Task，绑定描述与预期输出；CIO 任务通过 context 依赖前序任务结果。
"""

from crewai import Task


def create_miner_task(agent, symbol: str):
    """
    创建「量化与基本面矿工」任务。
    要求该 Agent 调用工具获取指定标的的量化技术数据与核心财务数据，
    输出一份结构化的财务与技术数据底稿。
    symbol: 6 位 A 股代码（如 600519），矿工工具仅支持代码不支持公司名称。
    """
    return Task(
        description=f"""你负责为目标标的收集并整理客观数据。请务必调用你拥有的工具完成以下工作：
1. 使用「获取A股技术面数据」工具，获取股票代码为 {symbol} 的 A 股近半年日 K 线及技术指标（20/60 日均线、MACD、RSI、布林带）。
2. 使用「获取A股基本面与财务数据」工具，获取股票代码为 {symbol} 的核心财务数据（市盈率 PE-TTM、营收增长率、现金流状况）。
请将上述工具返回的原始数据整理成一份结构清晰、无主观评价的底稿，包含：技术面摘要、财务面摘要。""",
        expected_output="""一份结构化的财务与技术数据底稿，须包含且仅包含客观数据，不得掺杂主观评价或投资建议。建议结构：
【技术面数据】
- 标的代码、区间、复权方式
- 最新收盘价、MA20、MA60
- MACD（DIF、DEA、柱）
- RSI(14)
- 布林带（上/中/下轨）
【财务面数据】
- 市盈率(PE-TTM)
- 营收增长率
- 现金流状况
若某类数据抓取失败，请在底稿中如实注明「获取失败」及原因，不得编造。""",
        agent=agent,
    )


def create_macro_task(agent, symbol_or_company_name: str):
    """
    创建「宏观政策与逻辑研究员」任务。
    要求该 Agent 调用搜索工具，查找目标公司所处行业的宏观政策与业务逻辑，
    输出一段带有事实依据的宏观逻辑推理简报，并明确政策面顺风/逆风结论。
    symbol_or_company_name: 股票代码或公司名称，用于搜索与报告表述。
    """
    return Task(
        description=f"""你负责研判目标标的所处的宏观与政策环境。请务必调用你拥有的网络搜索工具完成以下工作：
1. 搜索与股票代码或公司「{symbol_or_company_name}」所在行业相关的最新国家宏观政策（如产业规划、财政与货币政策、行业监管等）。
2. 搜索该公司近期的核心业务动态、战略方向或重要经营事件。
3. 结合搜索结果，判断该公司实际业务与当前宏观风口（如：出海、新质生产力、设备更新、消费升级等）的契合度。
请基于检索到的事实与逻辑，撰写一份宏观逻辑推理简报，并在文末明确给出结论：政策面是「顺风」还是「逆风」；若存在「蹭概念」、业务与政策背离等风险，须明确写出。""",
        expected_output="""一段带有事实依据的宏观逻辑推理简报。须包含：
- 行业与公司相关的最新宏观政策要点（可引用检索结果）。
- 公司近期核心业务动态摘要。
- 业务与当前宏观风口的契合度分析。
- 明确结论：政策面为「顺风」或「逆风」；若存在蹭概念、业务与政策背离等情况，须单独指出，供后续决策一票否决参考。
全文以事实与逻辑为主，不做最终买卖建议。""",
        agent=agent,
    )


def create_cio_task(agent, symbol_or_company_name: str, context: list = None):
    """
    创建「首席投资总监」任务（灵魂任务）。
    要求 CIO 必须查阅前两个任务的结果，并严格执行「贵出如粪土，贱取如珠玉」的逻辑：
    极度冰点买入、极度泡沫清仓、逻辑不符一票否决。输出格式固定为三部分。
    symbol_or_company_name: 标的标识，用于战报表述。
    context: 前置任务列表，通常为 [miner_task, macro_task]，CIO 将据此整合并决策。
    """
    return Task(
        description=f"""你是最终决策者。请务必先完整阅读并理解前序两个任务输出的内容：
1. 「量化与基本面矿工」提供的财务与技术数据底稿（估值、PE-TTM、均线、MACD、RSI、布林带、营收与现金流等）。
2. 「宏观政策与逻辑研究员」提供的宏观逻辑推理简报（政策顺风/逆风、是否蹭概念、业务与政策是否背离）。
在此基础上，你必须严格执行「贵上极则反贱，贱下极则反贵。贵出如粪土，贱取如珠玉」的投资纪律：
- 极度冰点判定（买入触发）：PE 估值极低 + RSI 超卖 + 宏观政策顺风 + 基本面健康。
- 极度泡沫判定（清仓触发）：PE 估值畸高 + RSI 严重超买 + 市场情绪狂热（即便基本面尚可也须提示减仓）。
- 逻辑否决权：若宏观研究员指出该公司纯属蹭概念或业务与政策背离，则一票否决买入，不得给出买入建议。
请针对标的「{symbol_or_company_name}」整合上述信息，输出你的最终战报，且必须严格按下列三部分格式书写，不得遗漏或合并。""",
        expected_output="""你的输出必须且仅包含以下三个部分，每部分以标题开头，内容简明扼要、可执行：

【估值与周期定性】
- 当前估值水平（高/中/低/极低/畸高）及依据（如 PE-TTM、历史分位等）。
- 技术周期定性（如超卖/中性/超买、趋势强弱等）。

【宏观共振分析】
- 宏观与政策面结论（顺风/逆风）及与公司业务的匹配度。
- 是否触发「一票否决」条件（蹭概念、业务与政策背离等）。

【铁血操作指令】
- 明确、可执行的指令：例如「建议买入」「建议观望」「建议减仓/清仓」「一票否决、不建议参与」等，并简要说明理由（须与前两部分逻辑一致）。""",
        agent=agent,
        context=context or [],
    )


def create_all_tasks(miner_agent, macro_agent, cio_agent, symbol_or_company_name: str):
    """
    按顺序创建全部三个任务，并自动将矿工任务与宏观任务作为 CIO 任务的 context。
    返回 (miner_task, macro_task, cio_task)，可直接传入 Crew 的 tasks 列表。
    """
    miner_task = create_miner_task(miner_agent, symbol_or_company_name)
    macro_task = create_macro_task(macro_agent, symbol_or_company_name)
    cio_task = create_cio_task(
        cio_agent,
        symbol_or_company_name,
        context=[miner_task, macro_task],
    )
    return miner_task, macro_task, cio_task
