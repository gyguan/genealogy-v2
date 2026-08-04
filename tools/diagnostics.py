#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    REVIEW = "REVIEW"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str
    path: str | None = None

    def format(self) -> str:
        location = f" {self.path}:" if self.path else ""
        return f"[{self.severity.value}] {self.code}{location} {self.message}"


class Reporter:
    def __init__(self) -> None:
        self._items: list[Diagnostic] = []

    @property
    def items(self) -> tuple[Diagnostic, ...]:
        return tuple(self._items)

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(item for item in self._items if item.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(item for item in self._items if item.severity is Severity.WARNING)

    @property
    def reviews(self) -> tuple[Diagnostic, ...]:
        return tuple(item for item in self._items if item.severity is Severity.REVIEW)

    def add(self, severity: Severity, code: str, message: str, path: str | Path | None = None) -> None:
        normalized_path = str(path) if path is not None else None
        self._items.append(Diagnostic(severity, code, message, normalized_path))

    def error(self, code: str, message: str, path: str | Path | None = None) -> None:
        self.add(Severity.ERROR, code, message, path)

    def warning(self, code: str, message: str, path: str | Path | None = None) -> None:
        self.add(Severity.WARNING, code, message, path)

    def review(self, code: str, message: str, path: str | Path | None = None) -> None:
        self.add(Severity.REVIEW, code, message, path)

    def extend(self, values: Iterable[Diagnostic]) -> None:
        self._items.extend(values)

    def render(self, title: str) -> str:
        lines = [title]
        if not self._items:
            lines.append("No diagnostics.")
        else:
            for severity in (Severity.ERROR, Severity.WARNING, Severity.REVIEW):
                selected = [item for item in self._items if item.severity is severity]
                if not selected:
                    continue
                lines.append(f"{severity.value} ({len(selected)}):")
                lines.extend(f"- {item.format()}" for item in selected)
        lines.append(
            f"Summary: errors={len(self.errors)}, warnings={len(self.warnings)}, review-only={len(self.reviews)}"
        )
        return "\n".join(lines)

    def exit_code(self) -> int:
        return 1 if self.errors else 0
