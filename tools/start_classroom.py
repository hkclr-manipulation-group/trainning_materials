"""Start a local JupyterLab with project-local state and an explicit kernel."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def environment():
    state = ROOT / "outputs" / "jupyter"
    locations = {"JUPYTER_CONFIG_DIR": state / "config",
                 "JUPYTER_DATA_DIR": state / "data",
                 "JUPYTER_RUNTIME_DIR": state / "runtime",
                 "IPYTHONDIR": state / "ipython"}
    env = os.environ.copy()
    for key, path in locations.items():
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    kernel = locations["JUPYTER_DATA_DIR"] / "kernels" / "training-python"
    kernel.mkdir(parents=True, exist_ok=True)
    spec = {"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Training Python", "language": "python"}
    (kernel / "kernel.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    missing = [name for name in ("jupyterlab", "ipykernel", "ipywidgets", "numpy", "matplotlib")
               if importlib.util.find_spec(name) is None]
    if missing:
        print("Missing:", ", ".join(missing))
        print("Use the course virtual environment; install requirements-interactive.txt.")
        return 1
    if not 1 <= args.port <= 65535:
        parser.error("port must be in [1, 65535]")
    env = environment()
    if args.check:
        print("Ready:", sys.executable)
        print("Course:", ROOT)
        return 0
    command = [sys.executable, "-m", "jupyterlab", "--ServerApp.ip=127.0.0.1",
               f"--ServerApp.port={args.port}", f"--ServerApp.root_dir={ROOT}",
               "--ServerApp.default_url=/lab/tree/notebooks/00_start_here.ipynb",
               "--ServerApp.use_redirect_file=False"]
    if args.no_browser:
        command.append("--no-browser")
    try:
        return subprocess.call(command, cwd=ROOT, env=env)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
