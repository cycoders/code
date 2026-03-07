import pytest
from pathlib import Path

@pytest.fixture
def good_html():
    return '''<!DOCTYPE html><html lang="en"><head><title>Test Page</title><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><h1>Hello</h1><img src="x" alt="test"><a href="#">test link</a></body></html>'''

@pytest.fixture
def bad_lang_html():
    return '''<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hi</h1></body></html>'''

@pytest.fixture
def bad_img_html():
    return '''<!DOCTYPE html><html lang="en"><head><title>Test</title></head><body><img src="x"></body></html>'''
