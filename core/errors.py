from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    BAD_REQUEST = "BAD_REQUEST"
    ROUTING_FAILED = "ROUTING_FAILED"
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    AGENT_FAILED = "AGENT_FAILED"
    STATE_TRANSITION_INVALID = "STATE_TRANSITION_INVALID"
    RUN_NOT_FOUND = "RUN_NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
