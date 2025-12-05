"""
JSON Formatter for CLI output.
"""

import json
from dataclasses import is_dataclass, asdict
from typing import Any
from application.dto.analysis_response import AnalysisResponse


class JsonFormatter:
    """
    Formats command results as JSON.
    """

    @staticmethod
    def format(data: Any) -> str:
        """
        Convert data to JSON string.
        """
        return json.dumps(data, default=JsonFormatter._serializer, indent=2)

    @staticmethod
    def _serializer(obj: Any) -> Any:
        """Custom serialization for domain objects."""
        if is_dataclass(obj):
            return asdict(obj)
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)
