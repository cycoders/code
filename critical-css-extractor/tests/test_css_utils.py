import re
from critical_css_extractor.css_utils import minify_css, load_rules


class TestCSSUtils:
    def test_minify_css(self):
        css = """
        /* comment */
        .hero { background: white;  
        color: red } /* end */
        """
        minified = minify_css(css)
        expected = ".hero{background:white;color:red}"
        assert minified == expected

    def test_load_rules(self, sample_css):
        rules = load_rules([sample_css])
        assert len(rules) == 4
        selectors = [str(r.selectorList) for r in rules]
        assert ".hero" in "".join(selectors)
        assert "#title" in "".join(selectors)