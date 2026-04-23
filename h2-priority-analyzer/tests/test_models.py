from h2_priority_analyzer.models import NetlogEvent, PriorityInfo, Stream


def test_netlog_event():
    data = {
        "source_type": "HTTP2_STREAM",
        "source": {"id": 1},
        "type": "HTTP2_STREAM_RECV_PRIORITY",
        "time": 1000000,
        "params": {"dependency": 0, "weight": 201},
    }
    event = NetlogEvent.model_validate(data)
    assert event.time == 1000000
    assert event.source["id"] == 1


def test_priority_info():
    info = PriorityInfo(dependency=3, weight=100, exclusive=True)
    assert info.dependency == 3


def test_stream_name():
    s = Stream(id=1, url="https://ex.com/a")
    assert s.name == "https://ex.com/a"
    s.url = None
    assert s.name == "Stream-1"
