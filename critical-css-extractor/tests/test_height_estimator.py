from bs4 import BeautifulSoup
from critical_css_extractor.height_estimator import estimate_height, mark_above_fold


class TestHeightEstimator:
    def test_estimate_height(self):
        assert estimate_height("h1", {}) == 48
        assert estimate_height("div", {}) == 32
        assert estimate_height("unknown", {}) == 25

    def test_mark_above_fold(self, sample_soup):
        mark_above_fold(sample_soup, viewport_height=100)
        hero = sample_soup.find("header", class_="hero")
        title = sample_soup.find("h1", id="title")
        below = sample_soup.find("div", class_="below")
        assert hero.get("data-critical") == "1"
        assert title.get("data-critical") == "1"
        assert below.get("data-critical") != "1"