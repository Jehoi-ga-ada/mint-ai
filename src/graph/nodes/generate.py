from typing import Any, Dict

from src.graph.chains.generation import generation_chain
from src.graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    result = generation_chain.invoke(
        {"context": state["documents"], "question": state["question"]}
    )

    return {"generation": result}
