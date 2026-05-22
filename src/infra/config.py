from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_url: str
    debug: bool

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    langsmith_tracing: bool
    langsmith_endpoint: str
    langsmith_api_key: str
    langsmith_project: str

    gemini_api_key: str

    tavily_api_key: str


config = Config()
