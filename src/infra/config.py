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

    # Claude on Amazon Bedrock — preferred LLM; Gemini is the fallback. Leave
    # the bearer token empty to run on Gemini only.
    aws_bearer_token_bedrock: str = ""
    bedrock_region: str = "ap-southeast-3"
    bedrock_model_id: str = "global.anthropic.claude-haiku-4-5-20251001-v1:0"

    tavily_api_key: str

    # Price-data providers (optional; assets without a key fall back to manual prices)
    coinmarketcap_api_key: str = ""
    coingecko_api_key: str = ""
    metal_api_key: str = ""
    fx_api_key: str = ""

    # How long a cached price/FX snapshot is considered fresh (seconds).
    price_ttl_seconds: int = 3600


config = Config()
