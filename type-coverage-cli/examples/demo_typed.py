# Example: Full type coverage
def greet(name: str, age: int) -> str:
    """Greet user."""
    return f"Hello {name}, you are {age}!"

class User:
    def __init__(self, id: int) -> None:
        self.id = id

    def get_info(self) -> dict[str, int]:
        return {"id": self.id}

async def fetch_data(url: str) -> bytes:
    ...

print(greet("Alice", 30))
