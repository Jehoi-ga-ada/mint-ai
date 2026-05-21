from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client

client = Client()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

prompt_template = client.pull_prompt(
    "rlm/rag-prompt", dangerously_pull_public_prompt=True
)

generation_chain = prompt_template | llm | StrOutputParser()
