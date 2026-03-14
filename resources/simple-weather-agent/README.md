# simple-weather-agent

Small demo showing two simple tools: `get_weather(city)` and `get_current_time(city)`.

Details
- Uses the Open-Meteo geocoding and forecast APIs (no API key required).
- Demonstrates HTTP-backed tools and timezone handling for city lookups.

Dependencies
- Python 3.12+ and the project dependencies (see the repo `pyproject.toml`).

Quick test
```bash
# from the repo root
python -m venv .venv
source .venv/bin/activate
pip install -e .

# one-off invocation that loads the agent file and prints London's weather
python - <<'PY'
import runpy
mod = runpy.run_path("simple-weather-agent/agent.py")
print(mod['get_weather']('London'))
PY
```

Notes
- The example is intentionally small so you can inspect `agent.py` and adapt the tools. The module defines `root_agent` and two helper functions that are easy to wire into a CLI or a web demo.
