import asyncio
from chaos_proxy.stats import Stats


@pytest.mark.asyncio
async def test_stats_concurrency() -> None:
    stats = Stats()

    async def writer(dir: str, n: int):
        for _ in range(n):
            await stats.record_bytes(dir, 1024)

    await asyncio.gather(
        writer("req", 100),
        writer("resp", 100),
    )

    assert stats.req_bytes == 1024 * 100
    assert stats.resp_bytes == 1024 * 100


@pytest.mark.parametrize("drops,total,expected_pct", [(0, 100, 0.0), (5, 100, 0.05)])
def test_loss_pct(drops: int, total: int, expected_pct: float) -> None:
    stats = Stats()
    stats.drops_req = drops
    stats.req_bytes = total
    assert abs(stats.loss_pct - expected_pct) < 0.01
