import pytest
from pathlib import Path
from bs4 import BeautifulSoup


@pytest.fixture
def sample_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="styles.css">
    <style>.inline-hero { color: blue; }</style>
</head>
<body>
    <header class="hero">
        <h1 id="title">Above Fold</h1>
        <p class="lead">Critical content</p>
    </header>
    <div class="below">Below fold</div>
</body>
</html>
    """


@pytest.fixture
def sample_css() -> str:
    return """
.hero { background: white; }
#title { font-size: 48px; }
.lead { color: red; }
.below { display: none; }
.inline-hero { font-weight: bold; }
"""


@pytest.fixture
def sample_soup(sample_html: str) -> BeautifulSoup:
    return BeautifulSoup(sample_html, features="lxml")