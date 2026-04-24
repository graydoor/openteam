import pytest

from core.errors import AppError, ErrorCode
from core.models import RunStatus
from orchestrator.service import assert_transition


def test_valid_transition() -> None:
    assert_transition(RunStatus.QUEUED, RunStatus.ROUTING)
    assert_transition(RunStatus.ROUTING, RunStatus.RUNNING)
    assert_transition(RunStatus.RUNNING, RunStatus.SUCCEEDED)


def test_invalid_transition_raises() -> None:
    with pytest.raises(AppError) as exc_info:
        assert_transition(RunStatus.QUEUED, RunStatus.SUCCEEDED)
    assert exc_info.value.code == ErrorCode.STATE_TRANSITION_INVALID
