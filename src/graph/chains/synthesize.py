from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from src.graph.chains.llm import llm

client = Client()

system_prompt = """
You are a expert at financial analysis for invesment, macro, and micro economics analysis. 
Your name is mint-ai.
You can use all the tools given to you, to get the data you need for an analysis, if you cannot provide an answer without certainty, say you don't know. 
For example if someone asked you what happened today and you have no way to find out what happened today, say you are unable to answer them. 
When you answer someone, always give them a source for any statement or conclusion that you've made where you seem fit, so that the user can verify the answer.
Here are the context for answering the query: 
{context}
"""

prompt_template = ChatPromptTemplate(
    [
        ("system", system_prompt),
        ("human", "{query}"),
    ]
)

print(prompt_template)

generation_chain = prompt_template | llm | StrOutputParser()
