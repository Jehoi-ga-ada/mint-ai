import json
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from src.features.auth.deps import get_current_user
from src.features.chat.schema import ChatMessage, ChatRequest
from src.graph.graph import graph
from src.infra.models.user import User

router = APIRouter(prefix="/chat")


def build_context(money_context: str | None, now: datetime | None = None) -> str:
    """Per-request system context: today's date (the model has no clock, and
    'past week' web searches go stale without it) plus the user's on-device
    Money data when the app sends it."""
    today = (now or datetime.now()).strftime("%A, %Y-%m-%d")
    lines = [f"Today's date is {today}."]
    if money_context:
        lines.append(
            "The user's Money Manager data from their device (IDR, source of "
            f"truth for their cash accounts and spending):\n{money_context}"
        )
    return "\n\n".join(lines)


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


def to_langchain_messages(messages: list[ChatMessage]) -> list[BaseMessage]:
    """Map the client's thread onto LangChain messages. User turns with images
    become multimodal content blocks (Gemini accepts base64 data URLs)."""
    result: list[BaseMessage] = []
    for m in messages:
        if m.role == "assistant":
            result.append(AIMessage(content=m.content))
        elif m.images:
            blocks = [{"type": "text", "text": m.content}] + [
                {"type": "image_url", "image_url": {"url": url}} for url in m.images
            ]
            result.append(HumanMessage(content=blocks))
        else:
            result.append(HumanMessage(content=m.content))
    return result


@router.post("/stream")
async def chat_stream(req: ChatRequest, user: User = Depends(get_current_user)):
    async def sse():
        try:
            async for event in graph.astream_events(
                {
                    "messages": to_langchain_messages(req.messages),
                    "context": build_context(req.money_context),
                },
                config={"configurable": {"user_id": str(user.id)}},
                version="v2",
            ):
                if event["event"] == "on_chat_model_stream":
                    token = extract_text(event["data"]["chunk"].content)
                    if token:
                        yield f"data: {json.dumps({'content': token})}\n\n"
                elif event["event"] == "on_tool_start":
                    # Lets the client show activity ("Searching the web…")
                    # instead of a silent wait during tool roundtrips.
                    yield f"data: {json.dumps({'status': event.get('name', 'tool')})}\n\n"
        except Exception as exc:  # surface mid-stream failures to the client
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")
