from typing import Any, Dict

from langchain_core.messages import SystemMessage

from src.graph.chains.llm import llm
from src.graph.chains.synthesize import system_prompt
from src.graph.state import GraphState

SYSTEM_MESSAGE = SystemMessage(content=system_prompt)


def run_agent_reasoning(state: GraphState) -> Dict[str, Any]:
    response = llm.invoke([SYSTEM_MESSAGE, *state["messages"]])
    return {"messages": [response]}
