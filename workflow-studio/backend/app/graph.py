from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import ResearchState
from .nodes import (
    plan_node, search_node, analyze_node,
    write_node, review_node, output_node, revision_node
)


def route_after_review(state: ResearchState) -> str:
    """审核后的条件路由"""
    if state["review_status"] == "approved":
        return "output"
    elif state["review_status"] == "rejected":
        # 防止无限循环：最多3轮
        if state.get("iteration_count", 0) >= 3:
            return "output"  # 强制输出
        return "revision"
    return "review"  # 默认等待


def build_research_graph():
    """构建研究工作流图"""

    # 1. 创建状态图
    graph = StateGraph(ResearchState)

    # 2. 添加节点
    graph.add_node("plan", plan_node)
    graph.add_node("search", search_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("write", write_node)
    graph.add_node("review", review_node)
    graph.add_node("output", output_node)
    graph.add_node("revision", revision_node)

    # 3. 添加边（线性流程）
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "search")
    graph.add_edge("search", "analyze")
    graph.add_edge("analyze", "write")
    graph.add_edge("write", "review")

    # 4. 条件边（审核后的分支）
    graph.add_conditional_edges(
        "review",
        route_after_review,
        {
            "output": "output",
            "revision": "revision",
            "review": "review",
        }
    )

    # 5. 修订后回到搜索（循环）
    graph.add_edge("revision", "search")

    # 6. 输出后结束
    graph.add_edge("output", END)

    return graph


async def get_compiled_graph():
    """编译图并附带检查点持久化"""
    graph = build_research_graph()

    # SQLite 检查点（生产环境用 PostgreSQL）
    checkpointer = AsyncSqliteSaver.from_conn_string("./checkpoints.db")

    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["review"],  # 在审核节点前暂停
    )

    return compiled
