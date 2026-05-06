import pytest

from llm_prompt_playground.tokenizer import Tokenizer


def test_tokenizer_count():
    tokenizer = Tokenizer()
    assert tokenizer.count("Hello world") == 4
    assert tokenizer.count("") == 0
    assert tokenizer.count("a" * 1000) > 200


def test_messages_count():
    tokenizer = Tokenizer()
    messages = [
        {"role": "user", "content": "Hi"},
        {"role": "system", "content": "Hello"},
    ]
    assert tokenizer.count_messages(messages) == 4
