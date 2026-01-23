import asyncio
import logging
import random
import time
from contextlib import asynccontextmanager

from rich.console import Console

from .config import Config
from .stats import Stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def forward_stream(
    src: asyncio.StreamReader,
    dst: asyncio.StreamWriter,
    cfg: Config,
    stats: Stats,
    direction: str,  # 'req' or 'resp'
) -> None:
    try:
        while True:
            data = await src.read(4096)
            if not data:
                break

            # Packet loss: drop entire chunk
            if random.random() < cfg.loss:
                stats.record_drop(direction)
                logger.debug(f"Dropped {len(data)} bytes ({direction})")
                continue

            impaired_data = data

            # Duplication: send multiple times (rarely 2-3x)
            if random.random() < cfg.dup:
                dup_count = random.choice([2, 3])
                impaired_data = data * dup_count
                logger.debug(f"Duplicated x{dup_count} ({direction})")

            # Bandwidth throttle: uniform delay
            if cfg.bw_bytes_per_sec < float("inf"):
                delay_bw = len(impaired_data) / cfg.bw_bytes_per_sec
                await asyncio.sleep(delay_bw)

            # Latency + jitter: always applied
            jitter_delay = random.uniform(-cfg.jitter / 2, cfg.jitter / 2)
            total_delay = cfg.latency + jitter_delay
            if total_delay > 0:
                await asyncio.sleep(total_delay)

            dst.write(impaired_data)
            await dst.drain()
            stats.record_bytes(direction, len(data))

    except Exception as e:
        logger.warning(f"Forward error ({direction}): {e}")
    finally:
        dst.close()
        await dst.wait_closed()


async def handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    cfg: Config,
    stats: Stats,
) -> None:
    stats.conn_active += 1
    try:
        target_reader, target_writer = await asyncio.open_connection(cfg.target_host, cfg.target_port)
        logger.info(f"New connection: {client_writer.get_extra_info('peername')} -> {cfg.target_host}:{cfg.target_port}")

        # Bidirectional forward with impairments
        await asyncio.gather(
            forward_stream(client_reader, target_writer, cfg, stats, "req"),
            forward_stream(target_reader, client_writer, cfg, stats, "resp"),
            return_exceptions=True,
        )
    except Exception as e:
        logger.error(f"Client handler error: {e}")
    finally:
        stats.conn_active -= 1
        client_writer.close()
        await client_writer.wait_closed()


async def stats_display_loop(console: Console, stats: Stats) -> None:
    """Live updating stats table every 1s."""
    from rich.live import Live
from rich.table import Table
from rich.text import Text

    grid = Table.grid(expand=True)
    grid.add_column("Metric", justify="left", style="cyan")
    grid.add_column("Requests", justify="right")
    grid.add_column("Responses", justify="right")

    uptime = Text()

    with Live(grid, console=console, refresh_per_second=1, transient=True) as live:
        while True:
            elapsed = time.monotonic() - stats.start_time
            req_rate = stats.req_bytes / elapsed if elapsed else 0
            resp_rate = stats.resp_bytes / elapsed if elapsed else 0

            grid.rows = [
                (
                    "Bytes",
                    f"{stats.req_bytes / 1024**2:.1f} MiB",
                    f"{stats.resp_bytes / 1024**2:.1f} MiB",
                ),
                (
                    "Rate",
                    f"{req_rate / 1024:.1f} KiB/s",
                    f"{resp_rate / 1024:.1f} KiB/s",
                ),
                (
                    "Drops",
                    f"{stats.drops_req} ({stats.loss_pct:.1%})",
                    f"{stats.drops_resp} ({stats.loss_pct:.1%})",
                ),
                (
                    "Avg Latency",
                    f"{stats.avg_latency_req*1000:.0f}ms",
                    f"{stats.avg_latency_resp*1000:.0f}ms",
                ),
                ("Active Conns", str(stats.conn_active), ""),
            ]

            uptime.text = f"Uptime: {elapsed:.0f}s | Ctrl+C to stop"
            live.update(grid)
            await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(console: Console):
    stats = Stats()
    stats_task = asyncio.create_task(stats_display_loop(console, stats))
    try:
        yield stats
    finally:
        stats_task.cancel()
        try:
            await stats_task
        except asyncio.CancelledError:
            pass


def run_server(cfg: Config) -> None:
    console = Console()

    async def main_server():
        server_stats = Stats()
        async with lifespan(console):
            server = await asyncio.start_server(
                lambda r, w: handle_client(r, w, cfg, server_stats),
                "0.0.0.0",
                cfg.local_port,
            )
            addr = server.sockets[0].getsockname()
            logger.info(f"Server listening on {addr}")
            console.print(f"🌐 Proxy ready: [bold green]localhost:{cfg.local_port}[/bold green] -> {cfg.target_host}:{cfg.target_port}")

            async with server:
                await server.serve_forever()

    try:
        asyncio.run(main_server())
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
