from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, select_autoescape
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.plugins import InitPluginProtocol
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig

if TYPE_CHECKING:
    from litestar_saq_htmx.config import SaqHtmxConfig
    from litestar.config.app import AppConfig


def format_datetime_short(datetime_value: datetime) -> str:
    return datetime_value.strftime("%d %b %Y %H:%M:%S")  # pragma: no cover


def format_ts_short(ts: int) -> str:
    return format_datetime_short(datetime.fromtimestamp(ts / 1000, timezone.utc))  # pragma: no cover


def format_ts_from_epoch_short(ts_from_epoch: int) -> str:
    return format_datetime_short(datetime.fromtimestamp(ts_from_epoch, timezone.utc))  # pragma: no cover


class SaqHtmxPlugin(InitPluginProtocol):
    def __init__(self, config: SaqHtmxConfig):
        self.config = config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        from litestar_saq_htmx.controller import SaqHtmxController

        app_config.dependencies.update(
            {
                "saq_queue": Provide(
                    self.config.provide_saq_queue, sync_to_thread=False
                ),
            },
        )
        environment = Environment(
            loader=FileSystemLoader(str(Path(__file__).parent / "saq_templates")),
            lstrip_blocks=True,
            trim_blocks=True,
            autoescape=select_autoescape(
                enabled_extensions=("html", "jinja", "jinja2"),
                default_for_string=True,
            ),
        )
        environment.filters.update(
            {
                "format_ts_short": format_ts_short,
                "format_ts_from_epoch_short": format_ts_from_epoch_short,
            }
        )
        template_config = TemplateConfig(
            instance=JinjaTemplateEngine.from_environment(environment)
        )
        app_config.template_config = template_config
        app_config.static_files_config.append(
            StaticFilesConfig(
                directories=[Path(__file__).parent / "saq_static"],
                path="/static",
                name="saq_static",
            )
        )
        app_config.route_handlers.append(SaqHtmxController)
        app_config.lifespan.append(self.config.lifespan)
        return app_config
