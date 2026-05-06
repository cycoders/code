from llm_prompt_playground.evaluator import Evaluator


def test_evaluate():
    scores = Evaluator.evaluate("Great answer!", 10, 5)
    assert scores["efficiency"] == 0.5
    assert "repetition" in scores
    assert scores["confidence"] >= 0

    hedge_resp = "I think maybe it's good."
    scores = Evaluator.evaluate(hedge_resp, 1, 1)
    assert scores["hedge_ratio"] > 0
    assert scores["confidence"] < 1
