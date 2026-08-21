from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import ResearchState
from .nodes import (
    plan_node, search_node, analyze_node,
    write_node, output_node, revision_node
)

# 全局 checkpointer 实例（需要在 lifespan 中初始化）
_checkpointer = None
_checkpointer_ctx = None
_compiled_graph = None


def route_after_review(state: ResearchState) -> str:
    """审核后的条件路由"""
    if state["review_status"] == "approved":
        return "output"
    elif state["review_status"] == "rejected":
        # 防止无限循环：最多3轮
        if state.get("iteration_count", 0) >= 3:
            return "output"  # 强制输出
        return "revision"
    return "output"  # 默认进入输出（首次运行时 interrupt_before 会在此暂停）


def build_research_graph():
    """构建研究工作流图"""

    # 1. 创建状态图
    graph = StateGraph(ResearchState)

    # 2. 添加节点
    graph.add_node("plan", plan_node)
    graph.add_node("search", search_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("write", write_node)
    graph.add_node("output", output_node)
    graph.add_node("revision", revision_node)

    # 3. 添加边（线性流程）
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "search")
    graph.add_edge("search", "analyze")
    graph.add_edge("analyze", "write")

    # 4. 条件边（写作后根据审核结果分支）
    graph.add_conditional_edges(
        "write",
        route_after_review,
        {
            "output": "output",
            "revision": "revision",
        }
    )

    # 5. 修订后回到搜索（循环）
    graph.add_edge("revision", "search")

    # 6. 输出后结束
    graph.add_edge("output", END)

    return graph


async def init_checkpointer():
    """初始化检查点器（在应用 lifespan 中调用）"""
    global _checkpointer, _checkpointer_ctx
    _checkpointer_ctx = AsyncSqliteSaver.from_conn_string("./checkpoints.db")
    _checkpointer = await _checkpointer_ctx.__aenter__()
    return _checkpointer


async def cleanup_checkpointer():
    """清理检查点器"""
    global _checkpointer, _checkpointer_ctx
    if _checkpointer_ctx:
        await _checkpointer_ctx.__aexit__(None, None, None)
        _checkpointer = None
        _checkpointer_ctx = None


async def get_compiled_graph():
    """编译图并附带检查点持久化"""
    global _compiled_graph, _checkpointer

    if _compiled_graph is not None:
        return _compiled_graph

    if _checkpointer is None:
        await init_checkpointer()

    graph = build_research_graph()

    _compiled_graph = graph.compile(
        checkpointer=_checkpointer,
        interrupt_before=["output"],  # 在输出节点前暂停，等待人工审核
    )

    return _compiled_graph
