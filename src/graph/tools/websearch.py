from langchain_tavily import TavilySearch

from src.infra.config import config

websearch = TavilySearch(tavily_api_key=config.tavily_api_key)
