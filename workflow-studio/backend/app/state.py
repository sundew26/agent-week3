from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages


class ResearchState(TypedDict):
    """研究工作流的完整状态"""
    # 消息历史（LangGraph 内置 reducer）
    messages: Annotated[list, add_messages]

    # 工作流控制
    current_step: str                    # 当前执行节点
    iteration_count: int                 # 循环次数（防止无限循环）

    # 研究内容
    original_question: str               # 用户原始问题
    research_plan: list[str]             # 规划的子问题
    search_results: list[dict]           # 搜索结果
    analysis: str                        # 分析综合
    draft_report: str                    # 草稿报告
    final_report: str                    # 最终报告

    # 人工审核
    review_status: Literal["pending", "approved", "rejected", ""]
    review_feedback: str                 # 审核意见

    # 元数据
    workflow_id: str
    started_at: str
    completed_at: str
