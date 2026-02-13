from stacktrace_collapser.models import Frame, Stacktrace


def test_frame_model_copy():
    frame = Frame(file="test.py", line=42, func="test")
    copied = frame.model_copy(update={"count": 5})
    assert copied.count == 5
    assert copied.file == "test.py"


def test_stacktrace():
    st = Stacktrace(language="python", frames=[])
    assert st.language == "python"
