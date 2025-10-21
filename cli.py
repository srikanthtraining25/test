from coding_agents.state import CodingState
from coding_agents.graph import build_graph
import argparse


def main():
    parser = argparse.ArgumentParser(description="Run LangGraph coding agents on a task")
    parser.add_argument("task", nargs="?", default="Write a Python function add(a, b) that returns their sum.")
    args = parser.parse_args()

    state = CodingState(task=args.task)
    app = build_graph()
    raw_result = app.invoke(state)
    # LangGraph returns a plain dict; normalize to our model
    result = raw_result if isinstance(raw_result, CodingState) else CodingState.model_validate(raw_result)

    print("History:")
    for h in result.history:
        print(" -", h)

    print("\nCode:\n")
    print(result.code)

    print("\nTests:\n")
    print(result.tests)

    print("\nTest Result:")
    print(result.test_output)
    print("Status:", result.status)


if __name__ == "__main__":
    main()
