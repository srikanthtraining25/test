from __future__ import annotations
from typing import Tuple
import re
import textwrap
from .state import CodingState


def intake_agent(state: CodingState) -> CodingState:
    task = (state.task or "").strip()
    normalized = re.sub(r"\s+", " ", task)
    new_state = state.model_copy(update={
        "normalized_task": normalized,
        "status": "intake_done",
    })
    new_state.append_history(f"Intake: task received -> {normalized}")
    return new_state


def planner_agent(state: CodingState) -> CodingState:
    task = state.normalized_task
    target = "Python function"
    inferred_name = infer_function_name(task)
    plan_lines = [
        f"Goal: Implement {target} to satisfy: '{task}'.",
        "Steps:",
        "1) Identify IO (function name, parameters, return).",
        "2) Implement function using simple, correct Python.",
        "3) Provide small self-tests to validate behavior.",
        "4) Iterate if tests fail.",
    ]
    if inferred_name:
        plan_lines.append(f"Inferred function name: {inferred_name}")

    plan = "\n".join(plan_lines)
    new_state = state.model_copy(update={
        "plan": plan,
        "status": "plan_done",
    })
    new_state.append_history("Planner: plan prepared")
    return new_state


def infer_function_name(task: str) -> str:
    # Very small heuristic mapper for demo purposes
    lower = task.lower()
    if "add" in lower or "sum" in lower:
        return "add"
    if "factorial" in lower:
        return "factorial"
    if "fibonacci" in lower:
        return "fibonacci"
    if "sort" in lower:
        return "sort_numbers"
    if "reverse" in lower and "string" in lower:
        return "reverse_string"
    return "solve"


def coder_agent(state: CodingState) -> CodingState:
    task = state.normalized_task.lower()
    func_name = infer_function_name(task)

    code = generate_solution_code(func_name, task)
    tests = generate_tests(func_name, task)

    new_state = state.model_copy(update={
        "code": code,
        "tests": tests,
        "status": "code_done",
    })
    new_state.append_history(f"Coder: code generated for {func_name}")
    return new_state


def generate_solution_code(func_name: str, task: str) -> str:
    # Provide simple deterministic implementations
    if func_name == "add":
        body = textwrap.dedent(
            f"""
            def add(a: float, b: float) -> float:
                return a + b
            """
        )
    elif func_name == "factorial":
        body = textwrap.dedent(
            """
            def factorial(n: int) -> int:
                if n < 0:
                    raise ValueError("n must be non-negative")
                result = 1
                for i in range(2, n + 1):
                    result *= i
                return result
            """
        )
    elif func_name == "fibonacci":
        body = textwrap.dedent(
            """
            def fibonacci(n: int) -> int:
                if n < 0:
                    raise ValueError("n must be non-negative")
                a, b = 0, 1
                for _ in range(n):
                    a, b = b, a + b
                return a
            """
        )
    elif func_name == "sort_numbers":
        body = textwrap.dedent(
            """
            from typing import List
            
            def sort_numbers(values: List[float]) -> List[float]:
                return sorted(values)
            """
        )
    elif func_name == "reverse_string":
        body = textwrap.dedent(
            """
            def reverse_string(s: str) -> str:
                return s[::-1]
            """
        )
    else:
        # default safe template
        body = textwrap.dedent(
            """
            def solve(*args, **kwargs):
                raise NotImplementedError("This demo supports add, factorial, fibonacci, sort_numbers, reverse_string")
            """
        )

    module = f'"""Auto-generated solution for: {task}"""\n\n' + body.lstrip()
    return module


def generate_tests(func_name: str, task: str) -> str:
    if func_name == "add":
        tests = textwrap.dedent(
            """
            def run_tests(module):
                assert module.add(2, 3) == 5
                assert module.add(-1, 1) == 0
                assert module.add(0, 0) == 0
                return "ok"
            """
        )
    elif func_name == "factorial":
        tests = textwrap.dedent(
            """
            def run_tests(module):
                assert module.factorial(0) == 1
                assert module.factorial(5) == 120
                return "ok"
            """
        )
    elif func_name == "fibonacci":
        tests = textwrap.dedent(
            """
            def run_tests(module):
                assert module.fibonacci(0) == 0
                assert module.fibonacci(1) == 1
                assert module.fibonacci(7) == 13
                return "ok"
            """
        )
    elif func_name == "sort_numbers":
        tests = textwrap.dedent(
            """
            def run_tests(module):
                assert module.sort_numbers([3,1,2]) == [1,2,3]
                assert module.sort_numbers([]) == []
                return "ok"
            """
        )
    elif func_name == "reverse_string":
        tests = textwrap.dedent(
            """
            def run_tests(module):
                assert module.reverse_string("abc") == "cba"
                assert module.reverse_string("") == ""
                return "ok"
            """
        )
    else:
        tests = textwrap.dedent(
            """
            def run_tests(module):
                return "no-tests"
            """
        )
    return tests


def tester_agent(state: CodingState) -> CodingState:
    code = state.code
    tests = state.tests
    result, output = run_code_and_tests(code, tests)
    new_state = state.model_copy(update={
        "test_passed": result,
        "test_output": output,
        "status": "test_passed" if result else "test_failed",
        "iterations": state.iterations + 1,
    })
    new_state.append_history("Tester: tests " + ("passed" if result else "failed"))
    return new_state


def run_code_and_tests(code: str, tests: str) -> Tuple[bool, str]:
    # Execute generated code and tests in isolated namespaces
    solution_globals = {"__builtins__": __builtins__}
    try:
        exec(code, solution_globals)
    except Exception as e:
        return False, f"Code execution error: {e!r}"

    test_globals = {}
    try:
        exec(tests, test_globals)
        run_tests = test_globals.get("run_tests")
        if not callable(run_tests):
            return False, "No run_tests found in tests"
        result = run_tests(type("Module", (), solution_globals))
        return True, f"Tests OK: {result}"
    except AssertionError as ae:
        return False, f"Assertion failed: {ae!r}"
    except Exception as e:
        return False, f"Test execution error: {e!r}"
