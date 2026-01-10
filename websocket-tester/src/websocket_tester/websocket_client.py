import asyncio
import json
import logging
from typing import Dict, Optional

import websockets

logger = logging.getLogger(__name__)

class WSClient:
    """Async WebSocket client with connect/send/recv/close."""

    def __init__(
        self,
        uri: str,
        headers: Optional[Dict[str, str]] = None,
        ping_interval: float = 20.0,
    ) -> None:
        self.uri = uri
        self.headers = headers or {}
        self.ping_interval = ping_interval
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self) -> None:
        """Connect with ping/pong enabled."""
        self._ws = await asyncio.wait_for(
            websockets.connect(
                self.uri,
                extra_headers=self.headers,
                ping_interval=self.ping_interval,
                ping_timeout=10,
                close_timeout=10,
            ),
            timeout=5.0,
        )
        logger.info(f"Connected: {self.uri}")

    async def send(self, message: str) -> None:
        """Send text message."""
        if not self._ws or self._ws.closed:
            raise RuntimeError("Not connected")
        await self._ws.send(message)
        logger.debug(f"TX: {message[:100]}")

    async def recv(self) -> Optional[str]:
        """Non-blocking recv (0.1s timeout)."""
        if not self._ws or self._ws.closed:
            return None
        try:
            msg = await asyncio.wait_for(self._ws.recv(), timeout=0.1)
            logger.debug(f"RX: {len(msg)}B")
            return msg
        except (asyncio.TimeoutError, websockets.ConnectionClosed):
            return None

    async def close(self) -> None:
        """Graceful close."""
        if self._ws:
            try:
                await self._ws.close(code=1000)
            except:
                pass
            self._ws = None
            logger.info("Disconnected")

    @property
    def connected(self) -> bool:
        return self._ws is not None and not self._ws.closed