from gc_tuning_advisor.recommender import recommend

def test_recommend_returns_tuple():
    assert len(recommend({})) == 3