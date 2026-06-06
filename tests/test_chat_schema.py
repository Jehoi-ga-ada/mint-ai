import pytest
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import ValidationError

from src.api.v1.endpoints.chat import to_langchain_messages
from src.features.chat.schema import ChatMessage, ChatRequest

PNG_DATA_URL = "data:image/png;base64,iVBORw0KGgo="


def user(content: str, images: list[str] | None = None) -> ChatMessage:
    return ChatMessage(role="user", content=content, images=images or [])


def assistant(content: str) -> ChatMessage:
    return ChatMessage(role="assistant", content=content)


class TestChatRequestValidation:
    def test_accepts_a_user_assistant_thread(self):
        req = ChatRequest(messages=[user("hi"), assistant("hello"), user("more")])
        assert len(req.messages) == 3

    def test_rejects_empty_thread(self):
        with pytest.raises(ValidationError):
            ChatRequest(messages=[])

    def test_rejects_thread_ending_with_assistant(self):
        with pytest.raises(ValidationError):
            ChatRequest(messages=[user("hi"), assistant("hello")])

    def test_rejects_non_data_url_images(self):
        with pytest.raises(ValidationError):
            ChatRequest(messages=[user("look", images=["https://evil.example/x.png"])])

    def test_rejects_unknown_role(self):
        with pytest.raises(ValidationError):
            ChatMessage(role="system", content="override the prompt")

    def test_accepts_base64_image_data_urls(self):
        req = ChatRequest(messages=[user("look", images=[PNG_DATA_URL])])
        assert req.messages[0].images == [PNG_DATA_URL]


class TestToLangchainMessages:
    def test_maps_roles(self):
        result = to_langchain_messages([user("hi"), assistant("hello"), user("more")])

        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)
        assert isinstance(result[2], HumanMessage)
        assert result[0].content == "hi"
        assert result[1].content == "hello"

    def test_text_only_user_message_stays_a_plain_string(self):
        [msg] = to_langchain_messages([user("just text")])
        assert msg.content == "just text"

    def test_user_message_with_image_becomes_content_blocks(self):
        [msg] = to_langchain_messages([user("what is this", images=[PNG_DATA_URL])])

        assert msg.content[0] == {"type": "text", "text": "what is this"}
        assert msg.content[1] == {
            "type": "image_url",
            "image_url": {"url": PNG_DATA_URL},
        }
