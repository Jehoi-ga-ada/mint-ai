from typing import Any, Dict

from langchain_core.messages import SystemMessage

from src.graph.chains.llm import llm
from src.graph.chains.synthesize import system_prompt
from src.graph.state import GraphState


def run_agent_reasoning(state: GraphState) -> Dict[str, Any]:
    context = state.get("context", "")
    content = f"{system_prompt}\n\n{context}" if context else system_prompt
    response = llm.invoke([SystemMessage(content=content), *state["messages"]])
    return {"messages": [response]}
