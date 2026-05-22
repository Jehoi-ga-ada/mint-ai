from langgraph.graph.state import START, StateGraph
from langgraph.prebuilt import tools_condition

from src.graph.nodes import run_agent_reasoning, tool_node
from src.graph.state import GraphState

from .const import REASONING, TOOLS

workflow = StateGraph(GraphState)
workflow.add_node(REASONING, run_agent_reasoning)
workflow.add_node(TOOLS, tool_node)

workflow.add_edge(START, REASONING)
workflow.add_conditional_edges(REASONING, tools_condition)
workflow.add_edge(TOOLS, REASONING)
graph = workflow.compile()

graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
