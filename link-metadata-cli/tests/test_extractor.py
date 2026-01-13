import pytest
from unittest.mock import patch, ANY
from link_metadata_cli.extractor import fetch_metadata
from link_metadata_cli.models import Metadata


@pytest.mark.parametrize(
    "url, expected_title",
    [
        ("https://test.com", "OG Title"),
        ("https://fallback.com", "Basic Title"),
    ],
)
def test_fetch_metadata(sample_html, mock_response, url, expected_title):
    with patch("requests_cache.CachedSession.get", return_value=mock_response):
        mock_response.text = sample_html
        meta = fetch_metadata(url)
        assert meta.title == expected_title
        assert meta.url == "https://test.com"
        assert meta.image == "https://test.com/og.jpg"


def test_fetch_metadata_twitter_fallback(sample_html, mock_response):
    # Remove OG title to test fallback
    html_no_og_title = sample_html.replace('<meta property="og:title" content="OG Title">', "")
    with patch("requests_cache.CachedSession.get", return_value=mock_response):
        mock_response.text = html_no_og_title
        meta = fetch_metadata("https://test.com")
        assert meta.title == "Twitter Title"


def test_fetch_metadata_jsonld_fallback(sample_html, mock_response):
    # Remove OG/twitter title
    html_no_titles = sample_html.replace(
        '<meta property="og:title" content="OG Title">', ""
    ).replace('<meta name="twitter:title" content="Twitter Title">', "")
    with patch("requests_cache.CachedSession.get", return_value=mock_response):
        mock_response.text = html_no_titles
        meta = fetch_metadata("https://test.com")
        assert meta.title == "JSON-LD Title"


def test_fetch_metadata_error(mock_response):
    with patch("requests_cache.CachedSession.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(RuntimeError):
            fetch_metadata("https://fail.com")


def test_image_absolute(sample_html, mock_response):
    with patch("requests_cache.CachedSession.get", return_value=mock_response):
        mock_response.text = sample_html
        meta = fetch_metadata("https://test.com")
        assert meta.image == "https://test.com/og.jpg"
