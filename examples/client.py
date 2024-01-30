import asyncio
import time
import random

from saq import CronJob, Queue


async def adder(ctx, *, a, b):
    await asyncio.sleep(1)
    return a + b


async def cron_job(ctx):
    await asyncio.sleep(1)
    return time.time()


settings = {
    "functions": [adder],
    "concurrency": 100,
    "cron_jobs": [CronJob(cron_job, cron="* * * * * */1")],
}


async def enqueue(func, **kwargs):
    queue = Queue.from_url("redis://localhost:6379")
    for _ in range(10000):
        await queue.enqueue(func, **{k: v() for k, v in kwargs.items()})


if __name__ == "__main__":
    asyncio.run(enqueue("adder", a=random.random, b=random.random))
