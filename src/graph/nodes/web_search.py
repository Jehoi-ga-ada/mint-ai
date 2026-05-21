from typing import Any, Dict

from langchain_classic.schema import Document
from langchain_tavily import TavilySearch

from graph.state import GraphState

web_search_tool = TavilySearch()


def web_search(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    documents = state["documents"]

    tavily_results = web_search_tool.invoke({"query": question})["results"]
    joined_result = "\n".join([tr["content"] for tr in tavily_results])

    web_results = Document(page_content=joined_result)
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]

    return {"documents": documents, "question": question}
