from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGES = 60
MAX_TEXT_CHARS = 20_000
MAX_IMAGES_PER_MESSAGE = 4
# ~6MB of base64 per image — keeps request bodies bounded.
MAX_IMAGE_DATA_URL_CHARS = 8_000_000
IMAGE_DATA_URL_PREFIXES = (
    "data:image/jpeg;base64,",
    "data:image/png;base64,",
    "data:image/webp;base64,",
    "data:image/heic;base64,",
)


class ChatMessage(BaseModel):
    """One turn of the conversation. The client owns the history (the graph has
    no checkpointer), so every request replays the full thread — which is what
    makes client-side edit/undo possible."""

    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_TEXT_CHARS)
    images: list[str] = Field(default_factory=list, max_length=MAX_IMAGES_PER_MESSAGE)

    @field_validator("images")
    @classmethod
    def validate_images(cls, images: list[str]) -> list[str]:
        for url in images:
            if not url.startswith(IMAGE_DATA_URL_PREFIXES):
                raise ValueError("images must be base64 data URLs (jpeg/png/webp/heic)")
            if len(url) > MAX_IMAGE_DATA_URL_CHARS:
                raise ValueError("image too large")
        return images


MAX_MONEY_CONTEXT_CHARS = 20_000


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=MAX_MESSAGES)
    # Compact JSON summary of the user's on-device Money data — the server has
    # no copy (Money Manager is offline-first), so the app sends it along.
    money_context: str | None = Field(default=None, max_length=MAX_MONEY_CONTEXT_CHARS)

    @field_validator("messages")
    @classmethod
    def last_message_from_user(cls, messages: list[ChatMessage]) -> list[ChatMessage]:
        if messages and messages[-1].role != "user":
            raise ValueError("last message must be from the user")
        return messages
