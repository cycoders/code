from cache_policy_advisor.recommender import recommend

def test_recommend_low_hit():
    assert 'stale-while-revalidate' in recommend({'hit_rate': 0.4})['Cache-Control']