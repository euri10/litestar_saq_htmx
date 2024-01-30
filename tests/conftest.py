from litestar import Litestar
import pytest

from typing import AsyncIterator, cast
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from litestar_saq_htmx.config import SaqHtmxConfig
from litestar_saq_htmx.plugin import SaqHtmxPlugin


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def app_test() -> AsyncIterator[Litestar]:
    saq_html = SaqHtmxPlugin(config=SaqHtmxConfig())
    app = Litestar(plugins=[saq_html], debug=True)
    async with LifespanManager(app) as lsm:  # type: ignore
        lsm.app = cast(Litestar, lsm.app)  # type: ignore
        yield lsm.app  # type: ignore


@pytest.fixture
async def client(app_test: Litestar) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app_test, base_url="https://testserver") as c:
        yield c
