from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # Per-request context appended to the system prompt (today's date, the
    # user's on-device Money data, ...). Plain last-value channel.
    context: str
