import pytest
import ast
from route_extractor_cli.extractors.fastapi import FastAPIExtractor

@pytest.fixture
def parse_sample(sample_code):
    tree = ast.parse(sample_code)
    return tree
