"""
Base engine class for all Master Creator engines.

Provides common functionality:
- Claude API client initialization
- Student Model Interface access
- Logging and audit trails
- Cost tracking
- Error handling
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional

import anthropic
from anthropic import Anthropic

from ..student_model.interface import StudentModelInterface


class BaseEngine(ABC):
    """
    Abstract base class for all engines.

    All engines must:
    - Query student data through StudentModelInterface (NO direct DB access)
    - Use Claude API for LLM operations
    - Log all decisions for audit trails
    - Track costs and token usage
    """

    def __init__(
        self,
        student_model: Optional[StudentModelInterface] = None,
        anthropic_api_key: Optional[str] = None,
    ):
        """
        Initialize engine.

        Args:
            student_model: StudentModelInterface instance (creates new if None)
            anthropic_api_key: Anthropic API key (uses env var if None)
        """
        # Student Model access
        self.student_model = student_model or StudentModelInterface()

        # Claude API client
        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)

        # Configuration
        self.model = os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

        # Cost tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

        # Audit log
        self.audit_log = []

    @abstractmethod
    def generate(self, **kwargs) -> Dict:
        """
        Main generation method - must be implemented by each engine.

        Args:
            **kwargs: Engine-specific parameters

        Returns:
            Dict with generated content
        """
        pass

    def _call_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Call Claude API with prompt caching support.

        Args:
            system_prompt: System instructions
            user_prompt: User query
            max_tokens: Override default max_tokens
            temperature: Override default temperature

        Returns:
            Claude's response text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # Track usage
            usage = response.usage
            self.total_input_tokens += usage.input_tokens
            self.total_output_tokens += usage.output_tokens

            # Calculate cost (approximate - adjust based on actual pricing)
            input_cost = (usage.input_tokens / 1_000_000) * 3.0  # $3/million input tokens
            output_cost = (usage.output_tokens / 1_000_000) * 15.0  # $15/million output tokens
            request_cost = input_cost + output_cost
            self.total_cost += request_cost

            # Log
            self._log_decision(
                f"Claude API call: {usage.input_tokens} in, {usage.output_tokens} out, ${request_cost:.4f}"
            )

            return response.content[0].text

        except anthropic.APIError as e:
            self._log_decision(f"Claude API error: {str(e)}", level="error")
            raise

    def _log_decision(self, message: str, level: str = "info", metadata: Optional[Dict] = None):
        """
        Log a decision for audit trail (FERPA compliance).

        Args:
            message: Log message
            level: Log level (info, warning, error)
            metadata: Additional metadata
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "engine": self.__class__.__name__,
            "level": level,
            "message": message,
            "metadata": metadata or {},
        }
        self.audit_log.append(log_entry)

    def get_cost_summary(self) -> Dict:
        """
        Get cost and usage summary.

        Returns:
            Dict with token counts and cost
        """
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
        }

    def get_audit_log(self) -> list:
        """
        Get complete audit log for compliance.

        Returns:
            List of log entries
        """
        return self.audit_log

    def reset_tracking(self):
        """Reset cost and usage tracking."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.audit_log = []
