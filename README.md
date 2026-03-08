# AI-Stock-Agent
基于 CrewAI 的多智能体 A 股投研系统。集成量化基本面提取、宏观政策检索与 CIO 深度推理，一键生成交互式终极投资战报。完美支持 DeepSeek、Qwen、智谱等国产大模型。
# 📈 AI-Stock-Agent 智能投研委员会

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CrewAI](https://img.shields.io/badge/Framework-CrewAI-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![LLM](https://img.shields.io/badge/LLM-DeepSeek%20%7C%20Qwen%20%7C%20Zhipu-brightgreen)

**AI-Stock-Agent** 是一个基于 [CrewAI](https://github.com/joaomdmoura/crewai) 框架构建的多智能体（Multi-Agent）A 股智能投研系统。它通过模拟真实投资机构的协作流程，自动完成数据抓取、宏观分析与终极决策，为投资者提供一份结构化、有深度、防瞎编的终极投资战报。

## ✨ 核心亮点

* 🤖 **三位一体的特工团队**：完美复刻机构投研流程（量化矿工 + 宏观研究员 + 首席投资总监）。
* 🧠 **无缝对接国产大模型**：内置 DeepSeek、阿里通义千问（Qwen）、智谱 GLM 的接口调度，彻底解决海外 API 封锁与高昂成本问题。
* 📊 **真实数据驱动防幻觉**：底层接入 [AkShare](https://akshare.xyz/)（新浪财经源）与 DuckDuckGo 搜索。特设“防幻觉最高指令”，数据获取失败时坚决拒绝做出投资建议。
* 🛡️ **工业级网络鲁棒性**：内置幽灵代理（Ghost Proxy）强力清除机制与梯队化 `max_iter` 循环限制，防止 Agent 陷入死循环或网络假死。
* 🎨 **优雅的 Web 交互界面**：基于 Streamlit 构建的现代前端，一键输入股票代码，实时展示 Agent 思考过程与最终战报。

## 👥 特工花名册 (Agents)

1.  ⛏️ **量化与基本面矿工 (Quant & Fundamental Miner)**
    * **工具**：AkShare 动态数据源。
    * **职责**：绝对理性的数据提取专家。负责提取目标 A 股的近半年 K 线衍生指标（MA、MACD、RSI、布林带）及核心财务数据（PE-TTM、营收增长、现金流）。
2.  🔍 **宏观政策与逻辑研究员 (Macro Policy Analyst)**
    * **工具**：DuckDuckGo Search。
    * **职责**：洞察国家大势与产业逻辑。检索目标公司最新的宏观政策与业务动态，研判政策面是“顺风”还是“逆风”，精准识别“蹭概念”风险。
3.  👔 **首席投资总监 (Chief Investment Officer, CIO)**
    * **工具**：纯逻辑推理（大脑）。
    * **职责**：践行“贵上极则反贱，贱下极则反贵”的逆向投资哲学。整合前序数据，出具包含【估值与周期定性】、【宏观共振分析】、【铁血操作指令】的终极战报。一票否决不合格标的。

## 🚀 快速开始

### 1. 克隆项目与安装依赖
```bash
git clone https://github.com/你的用户名/AI-Stock-Agent.git
cd AI-Stock-Agent
pip install -r requirements.txt
```

### 2. 配置大模型 API 密钥
在项目根目录创建一个 `.env` 文件，填入你拥有的国产大模型 API Key（填入其中一个或多个即可）：
```env
# 智谱 AI (GLM-4-Flash 完全免费)
ZHIPU_API_KEY="your_zhipu_api_key_here"

# 阿里通义千问
QWEN_API_KEY="your_qwen_api_key_here"

# DeepSeek
DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

### 3. 启动 Web 交互界面
**⚠️ 注意：运行前请务必关闭电脑上的 VPN / 代理软件，以免触发国内财经数据源的防火墙拦截。**
```bash
streamlit run app.py
```

打开浏览器访问 `http://localhost:8501`，在左侧边栏选择你配置好的 LLM 厂商，输入 6 位股票代码（如 `300750` 或 `000858`），点击“开始深度研判”即可体验！

## 💡 投资哲学
本系统底层 Prompt 严格植入了《史记·货殖列传》中的商业智慧：
> *"贵上极则反贱，贱下极则反贵。贵出如粪土，贱取如珠玉。"*
系统旨在寻找基本面健康、宏观顺风，但受困于市场情绪导致技术面极度冰点（超卖）的“珠玉”标的，同时规避情绪狂热、估值畸高的“粪土”泡沫。

## ⚠️ 免责声明 (Disclaimer)
本项目仅供 AI 多智能体技术学习、研究与交流使用。系统生成的任何战报、数据摘要及操作指令均**不构成任何实质性的投资建议**。股市有风险，投资需谨慎，请对自己的账户负责。
