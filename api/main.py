from fastapi import FastAPI

from api.routes.execute import router as execute_router
from api.routes.stream import router as stream_router

from browser.bootstrap import ensure_cdp_running


app = FastAPI(
    title="Desktop Agent API"
)


@app.on_event("startup")
def startup():

    print(
        "Starting Chromium CDP..."
    )

    ensure_cdp_running()


app.include_router(execute_router)
app.include_router(stream_router)