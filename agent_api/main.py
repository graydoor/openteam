from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from agents.coder import CoderAgent
from agents.planner import PlannerAgent
from core.config import get_settings
from core.errors import AppError, ErrorCode
from core.models import ApiErrorResponse, ErrorBody, RunRequest, RunResponse, TraceEvent
from orchestrator.service import Orchestrator
from router.service import Router
from tracing.service import TraceRecorder

settings = get_settings()
tracer = TraceRecorder(log_level=settings.log_level)
router = Router()
agents = {
    "planner": PlannerAgent(settings),
    "coder": CoderAgent(settings),
}
orchestrator = Orchestrator(
    settings=settings,
    router=router,
    agents=agents,
    tracer=tracer,
)

app = FastAPI(title=settings.app_name)


@app.exception_handler(AppError)
def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    response = ApiErrorResponse(
        error=ErrorBody(code=exc.code, message=exc.message, details=exc.details),
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))


@app.exception_handler(RequestValidationError)
def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    response = ApiErrorResponse(
        error=ErrorBody(
            code=ErrorCode.BAD_REQUEST,
            message="Invalid request body",
            details={"validation_errors": exc.errors()},
        ),
    )
    return JSONResponse(status_code=422, content=response.model_dump(mode="json"))


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post("/runs", response_model=RunResponse)
def create_run(payload: RunRequest) -> RunResponse:
    return orchestrator.execute(payload)


@app.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str) -> RunResponse:
    run = orchestrator.get_run(run_id)
    if run is None:
        raise AppError(
            code=ErrorCode.RUN_NOT_FOUND,
            message=f"run_id '{run_id}' was not found",
            status_code=404,
            details={"run_id": run_id},
        )
    return run


@app.get("/traces/{trace_id}", response_model=list[TraceEvent])
def get_trace(trace_id: str) -> list[TraceEvent]:
    return tracer.get_events(trace_id)
