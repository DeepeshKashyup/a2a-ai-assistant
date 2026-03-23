"""Output safety guardrails — PII filtering, format enforcement, length capping.
"""

import re
import structlog

logger = structlog.get_logger()

# PII patterns to redact from LLM output
_PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b(\+1[-.\\s]?)?\(?\d{3}\)?[-.\\s]?\d{3}[-.\\s]?\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b"),
}

_REPLACEMENTS = {
    "email": "[EMAIL REDACTED]",
    "ssn": "[SSN REDACTED]",
    "phone": "[PHONE REDACTED]",
    "credit_card": "[CARD REDACTED]",
}


class OutputGuard:
    """Post-processes LLM output to ensure safety and policy compliance."""

    MAX_OUTPUT_LENGTH = 8000

    def filter(self, text: str) -> str:
        """Apply all output filters and return cleaned text.

        Args:
            text: Raw LLM output string.

        Returns:
            Filtered and safe output string.
        """
        text = self._redact_pii(text)
        text = self._truncate(text)
        logger.debug("output_guard_passed", output_length=len(text))
        return text

    def _redact_pii(self, text: str) -> str:
        """Replace PII patterns with safe placeholders."""
        for pii_type, pattern in _PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                logger.warning("pii_detected_in_output", pii_type=pii_type, count=len(matches))
                text = pattern.sub(_REPLACEMENTS[pii_type], text)
        return text

    def _truncate(self, text: str) -> str:
        """Truncate output if it exceeds the max allowed length."""
        if len(text) > self.MAX_OUTPUT_LENGTH:
            logger.warning("output_truncated", original_length=len(text), max=self.MAX_OUTPUT_LENGTH)
            return text[: self.MAX_OUTPUT_LENGTH] + "\n\n[Response truncated]"
        return text