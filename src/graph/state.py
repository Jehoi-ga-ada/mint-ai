from typing import List, TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of supporting document
    """

    question: str
    generation: str
    web_search: bool
    documents: List[str]
