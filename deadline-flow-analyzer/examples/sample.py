import asyncio

async def worker(deadline: float | None = None):
    await asyncio.sleep(0.1)  # missing propagation

async def orchestrator():
    await worker()  # should pass deadline