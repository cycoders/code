from orm_nplus1_detector.detectors.sqlalchemy import detect_sqlalchemy_nplus1

def test_no_false_positives():
    assert detect_sqlalchemy_nplus1('session.query(User)') == []