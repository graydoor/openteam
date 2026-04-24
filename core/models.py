from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from core.errors import ErrorCode


class TaskIntent(str, Enum):
    PLANNING = "planning"
    CODING = "coding"
    REVIEW = "review"


class RunStatus(str, Enum):
    QUEUED = "queued"
    ROUTING = "routing"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RouteDecision(BaseModel):
    intent: TaskIntent
    specialist: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    fallback: bool = False


class AgentOutput(BaseModel):
    summary: str
    actions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class RunRequest(BaseModel):
    task: str = Field(min_length=5, max_length=4000)
    context: dict[str, Any] = Field(default_factory=dict)


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    run_id: str
    trace_id: str
    status: RunStatus
    route: RouteDecision | None = None
    output: AgentOutput | None = None
    error: ErrorBody | None = None


class ApiErrorResponse(BaseModel):
    trace_id: str | None = None
    error: ErrorBody


class TraceEventType(str, Enum):
    RUN_STARTED = "run_started"
    ROUTED = "routed"
    AGENT_INVOKED = "agent_invoked"
    AGENT_RETRY = "agent_retry"
    RUN_FINISHED = "run_finished"
    RUN_FAILED = "run_failed"


class TraceEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str
    run_id: str
    event: TraceEventType
    status: RunStatus | None = None
    data: dict[str, Any] = Field(default_factory=dict)
