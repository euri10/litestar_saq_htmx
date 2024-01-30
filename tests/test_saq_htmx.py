from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
from unittest import mock

import pytest
from httpx import AsyncClient
from httpx_sse import aconnect_sse

from litestar_saq_htmx.controller import generate_events
from litestar_saq_htmx.plugin import (
    format_datetime_short,
    format_ts_short,
    format_ts_from_epoch_short,
)


@contextmanager
def mock_events():
    with mock.patch(
        "litestar_saq_htmx.controller.generate_events",
        partial(generate_events, timeout=0.5),
    ):
        yield


@pytest.mark.anyio
async def test_saq(client: AsyncClient) -> None:
    response = await client.get("/saq")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_saq_stream(client: AsyncClient) -> None:
    with mock_events():
        async with aconnect_sse(
            client, method="GET", url="/saq/stream"
        ) as event_source:
            events = [sse async for sse in event_source.aiter_sse()]
            assert events[0].event == "queues"
            assert events[1].event == "workers"
            assert events[2].event == "jobs"

