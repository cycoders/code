import tiktoken


class Tokenizer:
    """Tokenizer using cl100k_base (GPT-4 compatible)."""

    def __init__(self) -> None:
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def count_messages(self, messages: list[dict[str, str]]) -> int:
        """Count tokens for full messages list."""
        return sum(self.count(msg["content"]) for msg in messages)
