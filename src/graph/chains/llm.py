from langchain_google_genai import ChatGoogleGenerativeAI

from src.graph.tools import tools
from src.infra.config import config

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", temperature=0, api_key=config.gemini_api_key
).bind_tools(tools=tools)
