import pytest
from stacktrace_collapser.parsers import detect_language, parse, parsers
from stacktrace_collapser.models import Frame


@pytest.mark.parametrize("lang, preview", [
    ("python", 'File "app.py", line 10'),
    ("nodejs", 'at handle (app.js:10:5)'),
    ("java", 'at com.App.main(App.java:10)'),
    ("go", 'app.go:10 +0x12 main.main()'),
])
def test_detect_language(lang, preview):
    assert detect_language(preview) == lang


@pytest.mark.parametrize("content, lang, expected", [
    (
        '''
Traceback (most recent call last):
  File "app.py", line 10, in <module>
    handle()
  File "views.py", line 42, in handle
    1/0
''',
        "python",
        [Frame(file="views.py", line=42, func="handle()"), Frame(file="app.py", line=10, func="<module>")],
    ),
    (
        """
Error: boom
    at handle (views.js:42:5)
    at run (app.js:10:3)
    at handle (views.js:42:5)  # repeat
""",
        "nodejs",
        [
            Frame(file="views.js", line=42, func="handle", col=5),
            Frame(file="app.js", line=10, func="run", col=3),
            Frame(file="views.js", line=42, func="handle", col=5),
        ],
    ),
    (
        """
Exception: boom
\tat App.handle(Views.java:42)
\tat App.main(App.java:10)
""",
        "java",
        [
            Frame(file="Views.java", line=42, func="App.handle"),
            Frame(file="App.java", line=10, func="App.main"),
        ],
    ),
    (
        """
goroutine 1 [running]:
main.handle()
\tviews.go:42 +0x88
main.main()
\tapp.go:10 +0x55
""",
        "go",
        [
            Frame(file="views.go", line=42, func="main.handle()"),
            Frame(file="app.go", line=10, func="main.main()"),
        ],
    ),
])
def test_parse(content, lang, expected):
    frames = parse(content, lang)
    assert len(frames) == len(expected)
    for f, e in zip(frames, expected):
        assert f.file == e.file
        assert f.line == e.line
        assert f.func == e.func


def test_detect_unknown():
    with pytest.raises(ValueError, match="Unsupported"):
        detect_language("random text")


def test_parse_unknown_lang():
    with pytest.raises(ValueError, match="Unsupported language"):
        parse("content", "rust")
