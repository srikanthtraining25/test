import streamlit as st
from typing import Optional
from coding_agents.state import CodingState
from coding_agents.graph import build_graph
from rich.markdown import Markdown

st.set_page_config(page_title="LangGraph Coding Agents", page_icon="🧠", layout="centered")

st.title("🧠 LangGraph Coding Agents")

st.caption("Input a task, watch planning, coding, testing, and iterative correction.")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "state" not in st.session_state:
    st.session_state.state = CodingState()

with st.form("task_form"):
    task = st.text_input("Describe the coding task", value=st.session_state.state.task or "Write a Python function add(a, b) that returns their sum.")
    submitted = st.form_submit_button("Run Agents")

if submitted:
    # Reset state for a fresh run
    st.session_state.state = CodingState(task=task)
    app_state = st.session_state.state

    # Run the compiled graph which iterates via conditional edges
    result: CodingState = st.session_state.graph.invoke(app_state)
    st.session_state.state = result

state: CodingState = st.session_state.state

st.subheader("Progress")
if state.history:
    for line in state.history:
        st.write(f"- {line}")
else:
    st.info("No progress yet — submit a task above.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Generated Code")
    st.code(state.code or "", language="python")
with col2:
    st.subheader("Generated Tests")
    st.code(state.tests or "", language="python")

st.subheader("Test Result")
if state.status == "test_passed":
    st.success(state.test_output or "All tests passed")
elif state.status == "test_failed":
    st.error(state.test_output or "Tests failed")
else:
    st.info("Pending run.")

st.divider()

st.caption("Reference flow: input → plan → code → test → correct loop → complete")
