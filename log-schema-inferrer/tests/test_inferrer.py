from log_schema_inferrer.inferrer import infer_schema
import tempfile, os

def test_infers_datetime_and_message():
    with tempfile.TemporaryDirectory() as tmp:
        (open(os.path.join(tmp, "a.log"), "w")).write("2025-01-01 INFO hello\n")
        schema = infer_schema(tmp)
        assert "ts" in schema["fields"]

def test_confidence_scores():
    with tempfile.TemporaryDirectory() as tmp:
        f = open(os.path.join(tmp, "b.log"), "w")
        f.write("key=val\n" * 10)
        f.close()
        schema = infer_schema(tmp)
        assert schema["fields"]["key"]["confidence"] > 0.8