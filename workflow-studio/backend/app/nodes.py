from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json
from datetime import datetime

from .state import ResearchState
from .tools import web_search, academic_search
from .config import LLM_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY

llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=0.3,
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)


async def plan_node(state: ResearchState) -> dict:
    """规划节点：将用户问题拆解为研究子问题"""
    question = state["original_question"]

    response = await llm.ainvoke([
        SystemMessage(content="""你是一个研究规划专家。将用户的研究问题拆解为3-5个具体的子问题。
返回JSON数组格式：["子问题1", "子问题2", ...]
只返回JSON数组，不要有其他内容。"""),
        HumanMessage(content=f"研究问题：{question}")
    ])

    try:
        plan = json.loads(response.content)
        if not isinstance(plan, list):
            plan = [question]
    except json.JSONDecodeError:
        plan = [question]  # 降级处理

    return {
        "research_plan": plan,
        "current_step": "plan",
        "messages": [AIMessage(content=f"📋 研究规划完成，拆解为 {len(plan)} 个子问题")]
    }


async def search_node(state: ResearchState) -> dict:
    """搜索节点：针对每个子问题执行搜索"""
    results = []

    for sub_question in state["research_plan"]:
        # 调用搜索工具
        result = web_search.invoke({"query": sub_question})
        results.append({
            "query": sub_question,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })

    return {
        "search_results": results,
        "current_step": "search",
        "messages": [AIMessage(content=f"🔍 搜索完成，获取了 {len(results)} 条结果")]
    }


async def analyze_node(state: ResearchState) -> dict:
    """分析节点：综合搜索结果进行分析"""
    search_context = "\n\n".join([
        f"查询: {r['query']}\n结果: {r['result']}"
        for r in state["search_results"]
    ])

    response = await llm.ainvoke([
        SystemMessage(content="你是一个研究分析师。综合分析以下搜索结果，提取关键发现、识别矛盾点、形成结构化分析。"),
        HumanMessage(content=f"原始问题：{state['original_question']}\n\n搜索结果：\n{search_context}")
    ])

    return {
        "analysis": response.content,
        "current_step": "analyze",
        "messages": [AIMessage(content="📊 分析综合完成")]
    }


async def write_node(state: ResearchState) -> dict:
    """写作节点：生成研究报告"""
    feedback = ""
    if state.get("review_feedback"):
        feedback = f"\n\n⚠️ 上一版审核反馈（请针对性改进）：{state['review_feedback']}"

    response = await llm.ainvoke([
        SystemMessage(content="你是一个学术写作专家。基于分析结果撰写结构化的研究报告，包含摘要、关键发现、深入分析、结论与建议。使用Markdown格式。"),
        HumanMessage(content=f"问题：{state['original_question']}\n\n分析：{state['analysis']}{feedback}")
    ])

    return {
        "draft_report": response.content,
        "current_step": "write",
        "messages": [AIMessage(content="✍️ 研究报告草稿完成")]
    }


async def review_node(state: ResearchState) -> dict:
    """审核节点：等待人工审核（Human-in-the-loop）"""
    # 这个节点会暂停执行，等待人工输入
    # LangGraph 的 interrupt_before 机制会在此暂停
    return {
        "current_step": "review",
        "review_status": "pending",
        "messages": [AIMessage(content="⏸️ 报告已生成，等待人工审核...")]
    }


async def output_node(state: ResearchState) -> dict:
    """输出节点：最终报告"""
    return {
        "final_report": state["draft_report"],
        "current_step": "output",
        "completed_at": datetime.now().isoformat(),
        "messages": [AIMessage(content="✅ 研究报告已完成！")]
    }


async def revision_node(state: ResearchState) -> dict:
    """修订节点：根据反馈决定是否需要重新搜索"""
    iteration = state.get("iteration_count", 0) + 1
    return {
        "iteration_count": iteration,
        "current_step": "revision",
        "messages": [AIMessage(content=f"🔄 第 {iteration} 轮修订，根据反馈重新搜索...")]
    }
