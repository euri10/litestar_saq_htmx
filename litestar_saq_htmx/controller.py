import asyncio
import time

from jinja2 import Environment
from litestar import Controller, get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.exceptions import HTTPException
from litestar.response import Template, ServerSentEvent
from litestar.response.sse import ServerSentEventMessage
from litestar.status_codes import HTTP_202_ACCEPTED, HTTP_404_NOT_FOUND
from saq import Queue
from typing_extensions import AsyncIterable


class SaqHtmxController(Controller):
    path = "/saq"

    @get(
        [
            "/",
        ],
        name="saq_index",
    )
    async def saq_index(self, saq_queue: Queue) -> Template:
        queue_info = {saq_queue.name: await saq_queue.info()}
        return Template("index.html", context={"queue_info": queue_info})

    @get("/stream")
    async def stream(
        self, request: HTMXRequest, saq_queue: Queue, refresh_time: str = "1"
    ) -> ServerSentEvent:
        return ServerSentEvent(generate_events(request, saq_queue, float(refresh_time)))

    @get(
        path="/jobs/{job_id:str}",
        name="job_detail",
    )
    async def job_detail(self, saq_queue: Queue, job_id: str) -> Template:
        job = await saq_queue.job(job_id)
        return Template("job_detail.html", context={"job": job})

    @post(
        name="job_retry",
        path="/jobs/{job_id:str}/retry",
        status_code=HTTP_202_ACCEPTED,
    )
    async def job_retry(self, saq_queue: Queue, job_id: str) -> None:
        job = await saq_queue.job(job_id)
        if job:
            await job.retry("retried from ui")
        else:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Job not found")
        return

    @post(
        name="job_abort",
        path="/jobs/{job_id:str}/abort",
        status_code=HTTP_202_ACCEPTED,
    )
    async def job_abort(self, saq_queue: Queue, job_id: str) -> None:
        job = await saq_queue.job(job_id)
        if job:
            await job.abort("aborted from ui")
        else:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Job not found")
        return


async def generate_events(
    _request: HTMXRequest,
    _saq_queue: Queue,
    refresh_time: float,
    timeout: int | None = None,
) -> AsyncIterable[ServerSentEventMessage]:
    starting_time = time.time()
    while not timeout or time.time() - starting_time < timeout:
        if not _request.is_connected:
            break
        info = await _saq_queue.info(jobs=True)
        env: Environment = _request.app.template_engine.engine
        queue_info_html = env.get_template("queue_info.html").render(
            queue_info=info, request=_request
        )
        workers_html = env.get_template("workers.html").render(
            queue_info=info, request=_request
        )
        jobs_html = env.get_template("jobs.html").render(
            queue_info=info, request=_request
        )
        await asyncio.sleep(refresh_time)
        yield ServerSentEventMessage(
            data=queue_info_html, id=_saq_queue.name, event="queues"
        )
        yield ServerSentEventMessage(
            data=workers_html, id=_saq_queue.name, event="workers"
        )
        yield ServerSentEventMessage(data=jobs_html, id=_saq_queue.name, event="jobs")
