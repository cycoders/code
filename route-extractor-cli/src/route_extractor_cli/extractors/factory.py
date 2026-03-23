from .fastapi import FastAPIExtractor
from .flask import FlaskExtractor
from .django import DjangoExtractor


def get_extractor(framework: str):
    match framework.lower():
        case "fastapi":
            return FastAPIExtractor
        case "flask":
            return FlaskExtractor
        case "django":
            return DjangoExtractor
        case "auto":
            return FastAPIExtractor  # Default to most common
        case _:
            raise ValueError(f"Unknown framework: {framework}")
