# google-adk-learning
Hands-on examples and demos for building tool-enabled agents with the Google ADK.

This repository collects small, runnable examples, notebooks, and templates that demonstrate building, evaluating, and experimenting with agent-based workflows in Python.

**Highlights**
- **`academic_research_assistant`**: a fuller example agent for literature retrieval and analysis. See [academic_research_assistant](academic_research_assistant#L1).
- **`simple-weather-agent`**: a small, practical demo showing tool usage and HTTP-backed tools. See [simple-weather-agent](simple-weather-agent#L1).
- **`exercises/`** and **`kaggle/`**: notebooks and hands-on tasks that demonstrate testing and evaluation patterns. See [exercises](exercises#L1) and [kaggle](kaggle#L1).

**Quickstart**
Prerequisites: Python 3.12+, a virtual environment, and an internet connection for live demos.

```bash
# from the repo root
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Quick test**
Try a small one-off invocation that loads the `simple-weather-agent` file and calls `get_weather` (uses the Open-Meteo APIs):

```bash
python - <<'PY'
import runpy
mod = runpy.run_path("simple-weather-agent/agent.py")
print(mod['get_weather']('London'))
PY
```

**Why share this repo?**
- Contains end-to-end examples and notebooks showing real agent/tool interactions.
- Demonstrates practical knowledge of Python tooling, API integration, and agent design patterns.

**Resume blurb (example)**
Built `academic_research_assistant`: a Python agent framework for literature retrieval and analysis; additional demos and notebooks in this repo showcase multi-agent patterns and tool usage.

For details and runnable demos, start with [academic_research_assistant](academic_research_assistant#L1) and [simple-weather-agent](simple-weather-agent#L1).
