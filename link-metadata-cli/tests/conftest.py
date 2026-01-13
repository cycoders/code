import json
import pytest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup


@pytest.fixture
def mock_response():
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    type(resp).text = ""
    resp.url = "https://test.com"
    return resp


@pytest.fixture
def sample_html():
    return """
<html>
<head>
<title>Basic Title</title>
<meta name="description" content="Basic desc">
<meta property="og:title" content="OG Title">
<meta property="og:description" content="OG desc">
<meta property="og:image" content="/og.jpg">
<meta property="og:site_name" content="OG Site">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Twitter Title">
<meta name="twitter:image" content="/twitter.jpg">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"WebPage","name":"JSON-LD Title","description":"JSON-LD desc","image":["/json.jpg"]}
</script>
</head>
</html>
    """
