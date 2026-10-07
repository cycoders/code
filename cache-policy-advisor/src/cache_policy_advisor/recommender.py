def recommend(metrics):
    if metrics['hit_rate'] < 0.6:
        return {'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400'}
    return {'Cache-Control': 'public, max-age=86400'}