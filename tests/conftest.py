from litestar import Litestar
import pytest

from typing import AsyncIterator

from litestar.testing import AsyncTestClient

from litestar_saq_htmx.config import SaqHtmxConfig
from litestar_saq_htmx.plugin import SaqHtmxPlugin


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def app_test() -> AsyncIterator[Litestar]:
    saq_html = SaqHtmxPlugin(config=SaqHtmxConfig())
    app = Litestar(plugins=[saq_html], debug=True)
    yield app


@pytest.fixture
async def client(app_test: Litestar) -> AsyncIterator[AsyncTestClient]:
    async with AsyncTestClient(app=app_test, base_url="https://testserver") as c:
        yield c
