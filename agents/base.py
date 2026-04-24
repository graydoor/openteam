import re
from abc import ABC, abstractmethod
from typing import Iterable

from core.config import Settings
from core.models import AgentOutput

SENSITIVE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)password\s*[:=]\s*\S+"),
]


def _sanitize_text(text: str) -> str:
    sanitized = text
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


def _normalize_lines(values: Iterable[str], max_items: int = 8, max_chars: int = 200) -> list[str]:
    items: list[str] = []
    for value in values:
        line = _sanitize_text(value.strip())
        if not line:
            continue
        if len(line) > max_chars:
            line = f"{line[: max_chars - 3]}..."
        items.append(line)
        if len(items) >= max_items:
            break
    return items


class SpecialistAgent(ABC):
    name: str = "specialist"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    def run(self, task: str, context: dict) -> AgentOutput:
        raise NotImplementedError

    def _finalize(self, output: AgentOutput) -> AgentOutput:
        summary = _sanitize_text(output.summary.strip())
        if len(summary) > self.settings.max_output_chars:
            summary = f"{summary[: self.settings.max_output_chars - 3]}..."

        return AgentOutput(
            summary=summary,
            actions=_normalize_lines(output.actions),
            risks=_normalize_lines(output.risks),
            next_steps=_normalize_lines(output.next_steps),
        )
