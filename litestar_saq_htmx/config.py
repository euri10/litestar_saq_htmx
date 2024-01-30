from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from saq import Queue

if TYPE_CHECKING:
    from typing import AsyncGenerator
    from litestar import Litestar
    from litestar.datastructures import State


@dataclass
class SaqHtmxConfig:
    redis_url: str = "redis://localhost:6379"
    saq_app_state_key: str = "saq_queue"

    @asynccontextmanager
    async def lifespan(
        self,
        app: Litestar,
    ) -> AsyncGenerator[None, None]:
        saq_queue = Queue.from_url(self.redis_url)
        app.state.update({self.saq_app_state_key: saq_queue})
        try:
            yield
        finally:
            await saq_queue.disconnect()

    def provide_saq_queue(self, state: State) -> Queue:
        return cast("Queue", state.get(self.saq_app_state_key))
