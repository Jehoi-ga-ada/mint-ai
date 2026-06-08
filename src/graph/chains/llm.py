import os

from langchain_aws import ChatBedrockConverse
from langchain_google_genai import ChatGoogleGenerativeAI

from src.graph.tools import tools
from src.infra.config import config

# Gemini is always built — it's the fallback (and the sole model when Bedrock
# isn't configured).
_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", temperature=0, api_key=config.gemini_api_key
).bind_tools(tools=tools)


def _build_llm():
    """Prefer Claude on Bedrock, fall back to Gemini.

    `with_fallbacks` retries the same request against Gemini if the Bedrock
    call raises (auth/throttle/region outage) — so a Bedrock problem degrades
    to Gemini instead of failing the chat. With no Bedrock token configured we
    skip Bedrock entirely and run on Gemini alone.
    """
    if not config.aws_bearer_token_bedrock:
        return _gemini

    # boto3's bedrock-runtime client authenticates with this bearer token (no
    # SigV4/IAM needed); set it explicitly so it's present even if the process
    # env didn't export it.
    os.environ["AWS_BEARER_TOKEN_BEDROCK"] = config.aws_bearer_token_bedrock

    bedrock = ChatBedrockConverse(
        model=config.bedrock_model_id,
        region_name=config.bedrock_region,
        provider="anthropic",  # required: the `global.` profile id hides the provider
        temperature=0,
    ).bind_tools(tools=tools)

    return bedrock.with_fallbacks([_gemini])


llm = _build_llm()
