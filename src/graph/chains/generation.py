from langchain_core.output_parsers import StrOutputParser
from langsmith import Client

from src.graph.chains.llm import llm

client = Client()

prompt_template = client.pull_prompt(
    "rlm/rag-prompt", dangerously_pull_public_prompt=True
)

generation_chain = prompt_template | llm | StrOutputParser()
