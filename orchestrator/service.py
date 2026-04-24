from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from time import monotonic
from uuid import uuid4

from agents.base import SpecialistAgent
from core.config import Settings
from core.errors import AppError, ErrorCode
from core.models import (
    AgentOutput,
    ErrorBody,
    RouteDecision,
    RunRequest,
    RunResponse,
    RunStatus,
    TraceEventType,
)
from router.service import Router
from tracing.service import TraceRecorder

ALLOWED_TRANSITIONS = {
    RunStatus.QUEUED: {RunStatus.ROUTING, RunStatus.FAILED},
    RunStatus.ROUTING: {RunStatus.RUNNING, RunStatus.FAILED},
    RunStatus.RUNNING: {RunStatus.SUCCEEDED, RunStatus.FAILED},
    RunStatus.SUCCEEDED: set(),
    RunStatus.FAILED: set(),
}


def assert_transition(current: RunStatus, target: RunStatus) -> None:
    allowed = ALLOWED_TRANSITIONS[current]
    if target not in allowed:
        raise AppError(
            code=ErrorCode.STATE_TRANSITION_INVALID,
            message=f"Invalid run status transition: {current} -> {target}",
            status_code=500,
            details={"current": current.value, "target": target.value},
        )


class Orchestrator:
    def __init__(
        self,
        *,
        settings: Settings,
        router: Router,
        agents: dict[str, SpecialistAgent],
        tracer: TraceRecorder,
    ) -> None:
        self.settings = settings
        self.router = router
        self.agents = agents
        self.tracer = tracer
        self._runs: dict[str, RunResponse] = {}

    def get_run(self, run_id: str) -> RunResponse | None:
        return self._runs.get(run_id)

    def execute(self, request: RunRequest) -> RunResponse:
        run_id = f"run-{uuid4().hex}"
        trace_id = self.tracer.new_trace_id()
        run_started = monotonic()
        run = RunResponse(run_id=run_id, trace_id=trace_id, status=RunStatus.QUEUED)
        self._runs[run_id] = run

        self.tracer.emit(
            trace_id=trace_id,
            run_id=run_id,
            event=TraceEventType.RUN_STARTED,
            status=run.status,
            data={"task_preview": request.task[:100]},
        )

        try:
            self._set_status(run, RunStatus.ROUTING)
            decision = self.router.route(request.task)
            run.route = decision
            self.tracer.emit(
                trace_id=trace_id,
                run_id=run_id,
                event=TraceEventType.ROUTED,
                status=run.status,
                data=decision.model_dump(mode="json"),
            )

            self._set_status(run, RunStatus.RUNNING)
            agent = self._resolve_agent(decision)
            run.output = self._invoke_agent_with_retry(
                agent=agent,
                request=request,
                run_id=run_id,
                trace_id=trace_id,
            )
            self._set_status(run, RunStatus.SUCCEEDED)
            self.tracer.emit(
                trace_id=trace_id,
                run_id=run_id,
                event=TraceEventType.RUN_FINISHED,
                status=run.status,
                data={"latency_ms": int((monotonic() - run_started) * 1000)},
            )
            return run
        except AppError as exc:
            run.error = ErrorBody(code=exc.code, message=exc.message, details=exc.details)
            if run.status in (RunStatus.QUEUED, RunStatus.ROUTING, RunStatus.RUNNING):
                self._set_status(run, RunStatus.FAILED)
            self.tracer.emit(
                trace_id=trace_id,
                run_id=run_id,
                event=TraceEventType.RUN_FAILED,
                status=run.status,
                data={
                    "error_code": exc.code.value,
                    "message": exc.message,
                    "latency_ms": int((monotonic() - run_started) * 1000),
                },
            )
            return run
        except Exception as exc:
            run.error = ErrorBody(
                code=ErrorCode.INTERNAL_ERROR,
                message="Unexpected internal error",
                details={"exception": str(exc)},
            )
            if run.status in (RunStatus.QUEUED, RunStatus.ROUTING, RunStatus.RUNNING):
                self._set_status(run, RunStatus.FAILED)
            self.tracer.emit(
                trace_id=trace_id,
                run_id=run_id,
                event=TraceEventType.RUN_FAILED,
                status=run.status,
                data={
                    "error_code": ErrorCode.INTERNAL_ERROR.value,
                    "message": str(exc),
                    "latency_ms": int((monotonic() - run_started) * 1000),
                },
            )
            return run

    def _set_status(self, run: RunResponse, target: RunStatus) -> None:
        assert_transition(run.status, target)
        run.status = target

    def _resolve_agent(self, decision: RouteDecision) -> SpecialistAgent:
        agent = self.agents.get(decision.specialist)
        if agent is None:
            raise AppError(
                code=ErrorCode.AGENT_NOT_FOUND,
                message=f"Specialist agent '{decision.specialist}' is not registered",
                status_code=500,
                details={"specialist": decision.specialist},
            )
        return agent

    def _invoke_agent_with_retry(
        self,
        *,
        agent: SpecialistAgent,
        request: RunRequest,
        run_id: str,
        trace_id: str,
    ) -> AgentOutput:
        max_attempts = self.settings.max_retries + 1
        last_error: AppError | None = None

        for attempt in range(1, max_attempts + 1):
            attempt_started = monotonic()
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(agent.run, request.task, request.context)
                    result = future.result(timeout=self.settings.run_timeout_sec)
                self.tracer.emit(
                    trace_id=trace_id,
                    run_id=run_id,
                    event=TraceEventType.AGENT_INVOKED,
                    status=RunStatus.RUNNING,
                    data={
                        "agent": agent.name,
                        "attempt": attempt,
                        "outcome": "succeeded",
                        "latency_ms": int((monotonic() - attempt_started) * 1000),
                    },
                )
                return result
            except FuturesTimeoutError:
                last_error = AppError(
                    code=ErrorCode.AGENT_TIMEOUT,
                    message=f"Agent '{agent.name}' timed out after {self.settings.run_timeout_sec}s",
                    status_code=504,
                    details={"agent": agent.name, "attempt": attempt},
                )
                self.tracer.emit(
                    trace_id=trace_id,
                    run_id=run_id,
                    event=TraceEventType.AGENT_INVOKED,
                    status=RunStatus.RUNNING,
                    data={
                        "agent": agent.name,
                        "attempt": attempt,
                        "outcome": "timeout",
                        "latency_ms": int((monotonic() - attempt_started) * 1000),
                    },
                )
            except Exception as exc:
                last_error = AppError(
                    code=ErrorCode.AGENT_FAILED,
                    message=f"Agent '{agent.name}' execution failed",
                    status_code=500,
                    details={"agent": agent.name, "attempt": attempt, "exception": str(exc)},
                )
                self.tracer.emit(
                    trace_id=trace_id,
                    run_id=run_id,
                    event=TraceEventType.AGENT_INVOKED,
                    status=RunStatus.RUNNING,
                    data={
                        "agent": agent.name,
                        "attempt": attempt,
                        "outcome": "failed",
                        "latency_ms": int((monotonic() - attempt_started) * 1000),
                    },
                )

            if attempt < max_attempts and last_error is not None:
                self.tracer.emit(
                    trace_id=trace_id,
                    run_id=run_id,
                    event=TraceEventType.AGENT_RETRY,
                    status=RunStatus.RUNNING,
                    data={
                        "agent": agent.name,
                        "attempt": attempt,
                        "error_code": last_error.code.value,
                    },
                )

        if last_error is None:
            raise AppError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Agent execution failed without explicit error",
                status_code=500,
            )
        raise last_error
