from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from agent.orchestrator import Orchestrator
from utils.global_events import event_bus

import asyncio


router = APIRouter()

orchestrator = Orchestrator()


@router.get("/stream")
async def stream(query: str):

    async def event_generator():

        loop = asyncio.get_running_loop()

        task = loop.run_in_executor(
            None,
            orchestrator.run,
            query
        )

        while not task.done():

            while not event_bus.empty():

                message = event_bus.get()

                yield {
                    "event": "status",
                    "data": message
                }

            await asyncio.sleep(0.1)

        result = await task

        while not event_bus.empty():

            yield {
                "event": "status",
                "data": event_bus.get()
            }

        yield {
            "event": "result",
            "data": str(result)
        }

        yield {
            "event": "status",
            "data": "Completed"
        }

    return EventSourceResponse(
        event_generator()
    )