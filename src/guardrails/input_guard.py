"""Input validation guardrails — length limits, topic blocking, injection detection.
"""

import re
import structlog
from app.core.config import settings

logger = structlog.get_logger()

# Patterns that suggest prompt injection attempts
_INJECTION_PATTERNS = [
    r"ignore (previous|all|above|prior) instructions",
    r"you are now",
    r"act as (a|an) (?!assistant)",
    r"disregard (your|all) (previous|prior|system)",
    r"system prompt",
    r"<\|.*?\|>",          # common injection delimiters
    r"\[INST\]",
    r"\[\/INST\]",
]

_COMPILED_INJECTION = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


class InputGuardError(ValueError):
    """Raised when input fails a guardrail check."""
    pass


class InputGuard:
    """Validates user inputs before they reach the LLM or retrieval pipeline."""

    def __init__(self) -> None:
        self.max_length = settings.max_input_length
        self.blocked_topics = [t.lower() for t in settings.blocked_topics]

    def validate(self, text: str) -> None:
        """Run all input checks. Raises InputGuardError on failure.

        Args:
            text: The raw user input string.

        Raises:
            InputGuardError: If any check fails.
        """
        self._check_length(text)
        self._check_blocked_topics(text)
        self._check_injection(text)
        logger.debug("input_guard_passed", length=len(text))

    def _check_length(self, text: str) -> None:
        if len(text) > self.max_length:
            logger.warning("input_too_long", length=len(text), max=self.max_length)
            raise InputGuardError(
                f"Input too long: {len(text)} chars exceeds limit of {self.max_length}."
            )

    def _check_blocked_topics(self, text: str) -> None:
        text_lower = text.lower()
        for topic in self.blocked_topics:
            if topic in text_lower:
                logger.warning("blocked_topic_detected", topic=topic)
                raise InputGuardError(f"Input contains a blocked topic: '{topic}'.")

    def _check_injection(self, text: str) -> None:
        for pattern in _COMPILED_INJECTION:
            if pattern.search(text):
                logger.warning("injection_pattern_detected", pattern=pattern.pattern)
                raise InputGuardError("Input contains a potential prompt injection pattern.")