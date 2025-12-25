class Animal:
    """Base animal."""
    age: int = 0

    def __init__(self, age: int):
        self.age = age

    def speak(self) -> str:
        return "..."


class Mammal(Animal):
    fur_color: str

    @classmethod
    def from_birth(cls) -> "Mammal":
        return cls(0)


class Dog(Mammal):
    def bark(self) -> str:
        return "woof!"

    @staticmethod
    def is_friendly() -> bool:
        return True
