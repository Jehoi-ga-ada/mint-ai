from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi.routing import json
from langchain_core.messages import HumanMessage

from src.features.chat.schema import ChatRequest
from src.graph.graph import graph

router = APIRouter(prefix="/chat")


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    async def sse():
        async for event in graph.astream_events(
            {"messages": [HumanMessage(content=req.message)]},
            config=(
                {"configurable": {"thread_id": req.thread_id}}
                if req.thread_id
                else None
            ),
            version="v2",
        ):
            if event["event"] == "on_chat_model_stream":
                token = extract_text(event["data"]["chunk"].content)
                if token:
                    yield f"data: {json.dumps({'content': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")
