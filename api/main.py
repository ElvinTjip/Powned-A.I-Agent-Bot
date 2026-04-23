import os

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api.database import create_tables
from api.deps import NotAuthenticated, get_current_user
from api.routes import actions, auth, feed

app = FastAPI(title="PowNed Redactie Agent", docs_url=None, redoc_url=None)

app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"])
app.mount("/static", StaticFiles(directory="web/static"), name="static")

app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(actions.router)


@app.exception_handler(NotAuthenticated)
async def not_authenticated_handler(request, exc):
    return RedirectResponse(url="/login")


@app.on_event("startup")
async def startup():
    create_tables()
    from scheduler.scheduler import start as start_scheduler
    from scheduler.pipeline import run_pipeline
    start_scheduler(run_pipeline)


@app.on_event("shutdown")
async def shutdown():
    from scheduler.scheduler import stop as stop_scheduler
    stop_scheduler()


@app.post("/admin/run-pipeline")
async def trigger_pipeline(
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    from scheduler.pipeline import run_pipeline

    background_tasks.add_task(run_pipeline)
    return {"status": "started"}
