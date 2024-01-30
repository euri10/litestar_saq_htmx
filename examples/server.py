from litestar import Litestar

from litestar_saq_htmx.config import SaqHtmxConfig
from litestar_saq_htmx.plugin import SaqHtmxPlugin


saq_html = SaqHtmxPlugin(config=SaqHtmxConfig())
app = Litestar(plugins=[saq_html], debug=True)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app")
