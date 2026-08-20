import asyncio
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langgraph.types import Command

from .graph import get_compiled_graph
from .state import ResearchState
from .schemas import StartRequest, ReviewRequest

app = FastAPI(title="Workflow Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局图实例
_graph = None


async def get_graph():
    global _graph
    if _graph is None:
        _graph = await get_compiled_graph()
    return _graph


# ========== 启动工作流 ==========
@app.post("/api/workflow/start")
async def start_workflow(request: StartRequest):
    """启动研究工作流"""
    graph = await get_graph()
    workflow_id = str(uuid.uuid4())

    initial_state: ResearchState = {
        "messages": [],
        "current_step": "start",
        "iteration_count": 0,
        "original_question": request.question,
        "research_plan": [],
        "search_results": [],
        "analysis": "",
        "draft_report": "",
        "final_report": "",
        "review_status": "",
        "review_feedback": "",
        "workflow_id": workflow_id,
        "started_at": datetime.now().isoformat(),
        "completed_at": "",
    }

    config = {"configurable": {"thread_id": workflow_id}}

    async def event_stream():
        try:
            async for event in graph.astream_events(
                initial_state,
                config=config,
                version="v2",
            ):
                kind = event["event"]

                if kind == "on_chain_start":
                    node_name = event.get("name", "")
                    if node_name in ("plan", "search", "analyze", "write", "review", "output", "revision"):
                        yield f"data: {json.dumps({'type': 'node_start', 'node': node_name})}\n\n"

                elif kind == "on_chain_end":
                    node_name = event.get("name", "")
                    if node_name in ("plan", "search", "analyze", "write", "review", "output", "revision"):
                        output = event.get("data", {}).get("output", {})
                        yield f"data: {json.dumps({'type': 'node_end', 'node': node_name, 'output': str(output)[:500]})}\n\n"

                elif kind == "on_chat_model_stream":
                    # LLM 流式输出
                    chunk = event.get("data", {}).get("chunk", None)
                    if chunk and hasattr(chunk, 'content') and chunk.content:
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

                elif kind == "on_tool_end":
                    yield f"data: {json.dumps({'type': 'tool_result', 'data': str(event.get('data', ''))[:300]})}\n\n"

            # 检查是否暂停在 review 节点
            state = await graph.aget_state(config)
            if state.next:  # 有下一个待执行节点 = 被中断了
                yield f"data: {json.dumps({'type': 'interrupted', 'at': state.next[0] if state.next else 'review', 'workflow_id': workflow_id})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'completed'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ========== 人工审核 ==========
@app.post("/api/workflow/review")
async def submit_review(request: ReviewRequest):
    """提交人工审核结果，恢复工作流"""
    graph = await get_graph()
    config = {"configurable": {"thread_id": request.workflow_id}}

    # 更新状态中的审核结果
    update = {
        "review_status": request.status,
        "review_feedback": request.feedback,
    }

    async def event_stream():
        try:
            # 从中断点恢复，注入审核结果
            async for event in graph.astream_events(
                Command(update=update, resume=True),
                config=config,
                version="v2",
            ):
                kind = event["event"]
                if kind == "on_chain_start":
                    node_name = event.get("name", "")
                    if node_name in ("plan", "search", "analyze", "write", "review", "output", "revision"):
                        yield f"data: {json.dumps({'type': 'node_start', 'node': node_name})}\n\n"
                elif kind == "on_chain_end":
                    node_name = event.get("name", "")
                    if node_name in ("plan", "search", "analyze", "write", "review", "output", "revision"):
                        yield f"data: {json.dumps({'type': 'node_end', 'node': node_name})}\n\n"
                elif kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk", None)
                    if chunk and hasattr(chunk, 'content') and chunk.content:
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

            # 检查是否再次暂停在 review 节点
            state = await graph.aget_state(config)
            if state.next:
                yield f"data: {json.dumps({'type': 'interrupted', 'at': state.next[0] if state.next else 'review', 'workflow_id': request.workflow_id})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'completed'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ========== 获取工作流状态（检查点恢复） ==========
@app.get("/api/workflow/state/{workflow_id}")
async def get_workflow_state(workflow_id: str):
    """获取工作流当前状态（用于页面刷新后恢复）"""
    graph = await get_graph()
    config = {"configurable": {"thread_id": workflow_id}}

    state = await graph.aget_state(config)
    if state is None:
        raise HTTPException(404, "工作流不存在")

    return {
        "workflow_id": workflow_id,
        "values": {k: v for k, v in state.values.items() if k != "messages"},
        "next": list(state.next) if state.next else [],
        "is_interrupted": bool(state.next),
    }


# ========== 获取工作流图结构（供前端渲染） ==========
@app.get("/api/workflow/graph-structure")
async def get_graph_structure():
    """返回图结构供前端渲染"""
    return {
        "nodes": [
            {"id": "plan", "label": "📋 规划", "type": "plan", "position": {"x": 250, "y": 0}},
            {"id": "search", "label": "🔍 搜索", "type": "search", "position": {"x": 250, "y": 120}},
            {"id": "analyze", "label": "📊 分析", "type": "analyze", "position": {"x": 250, "y": 240}},
            {"id": "write", "label": "✍️ 写作", "type": "write", "position": {"x": 250, "y": 360}},
            {"id": "review", "label": "👤 审核", "type": "review", "position": {"x": 250, "y": 480}},
            {"id": "revision", "label": "🔄 修订", "type": "revision", "position": {"x": 500, "y": 300}},
            {"id": "output", "label": "✅ 输出", "type": "output", "position": {"x": 250, "y": 600}},
        ],
        "edges": [
            {"id": "e1", "source": "plan", "target": "search"},
            {"id": "e2", "source": "search", "target": "analyze"},
            {"id": "e3", "source": "analyze", "target": "write"},
            {"id": "e4", "source": "write", "target": "review"},
            {"id": "e5", "source": "review", "target": "output", "label": "通过"},
            {"id": "e6", "source": "review", "target": "revision", "label": "不通过"},
            {"id": "e7", "source": "revision", "target": "search"},
        ]
    }
