from __future__ import annotations
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class CodingState(BaseModel):
    task: str = Field(default="", description="Raw user task input")
    normalized_task: str = Field(default="", description="Normalized/clarified task")
    plan: str = Field(default="", description="High-level plan for coding the task")
    code: str = Field(default="", description="Generated code as a single Python module string")
    tests: str = Field(default="", description="Generated tests as a Python string")
    test_passed: bool = Field(default=False)
    test_output: str = Field(default="", description="Verbose test run output")
    iterations: int = Field(default=0, description="Number of code/test correction cycles performed")
    status: Literal[
        "idle",
        "intake_done",
        "plan_done",
        "code_done",
        "test_passed",
        "test_failed",
        "completed",
    ] = Field(default="idle")
    history: List[str] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)

    def append_history(self, message: str) -> None:
        self.history.append(message)
