from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """搜索互联网获取相关信息"""
    # 实际项目中替换为 Tavily / SerpAPI / Bing Search
    # 这里用模拟数据演示
    mock_results = {
        "agent": "AI Agent 是能够自主感知环境、做出决策并执行行动的系统。2026年，AI Agent 技术正在快速发展，主要趋势包括：多Agent协作、工具使用能力增强、长期记忆机制、以及更可靠的规划与推理能力。",
        "langgraph": "LangGraph 是一个用于构建有状态多Agent应用的框架，由 LangChain 团队开发。它支持条件分支、循环、人工审核等高级工作流模式，是目前构建复杂 AI Agent 系统的首选框架之一。",
        "rag": "RAG (检索增强生成) 通过检索外部知识来增强LLM回答。2026年的RAG技术已经演进到支持多模态检索、自适应分块、以及基于知识图谱的高级检索策略。",
        "llm": "大语言模型(LLM)在2026年继续向更大规模、更强推理能力发展。主要厂商包括OpenAI、Anthropic、Google等，开源模型如Llama系列也在快速追赶。",
        "multi-agent": "多Agent系统是指多个AI Agent协作完成复杂任务的架构。常见模式包括：分工协作、辩论式推理、层级管理等。LangGraph和CrewAI是主流的多Agent框架。",
    }
    for key, val in mock_results.items():
        if key in query.lower():
            return val
    return f"搜索 '{query}' 的结果：找到了3篇相关文献，核心观点包括该领域的最新研究进展表明技术正在快速发展，多个研究团队提出了创新性的解决方案。"


@tool
def academic_search(query: str) -> str:
    """搜索学术论文"""
    return f"学术论文搜索 '{query}': 找到5篇相关论文，最新发表于2026年。主要发现包括：1) 提出了新的方法论框架；2) 实验结果验证了有效性；3) 指出了未来研究方向。"
