from __future__ import annotations
from typing import Callable
from langgraph.graph import StateGraph, END
from .state import CodingState
from .agents import intake_agent, planner_agent, coder_agent, tester_agent


MAX_ITERS = 3


def build_graph() -> Callable[[CodingState], CodingState]:
    graph = StateGraph(CodingState)

    graph.add_node("intake", intake_agent)
    graph.add_node("plan", planner_agent)
    graph.add_node("code", coder_agent)
    graph.add_node("test", tester_agent)

    graph.set_entry_point("intake")

    graph.add_edge("intake", "plan")
    graph.add_edge("plan", "code")
    graph.add_edge("code", "test")

    def route_after_test(state: CodingState):
        if state.test_passed:
            return END
        if state.iterations >= MAX_ITERS:
            return END
        return "code"

    graph.add_conditional_edges("test", route_after_test)

    return graph.compile()
