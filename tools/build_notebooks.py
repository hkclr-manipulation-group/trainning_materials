"""Build notebooks from readable percent-format Python, using only stdlib.

Authoring sources are in notebooks/source; notebook edits are not overwritten
unless this tool is explicitly run. Each file gets the same setup cell.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SETUP = '''from pathlib import Path
import sys, math, csv, json

# Locate the course even when the kernel starts in notebooks/.
ROOT = next((p for p in (Path.cwd(), *Path.cwd().parents)
             if (p / "labs" / "course_lab.py").is_file()), None)
if ROOT is None:
    raise RuntimeError("Open this notebook inside the complete trainning_materials folder.")
sys.path.insert(0, str(ROOT / "labs"))
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, Image, HTML
import ipywidgets as widgets
from course_lab import fk, ik, encode_frame, decode_frame, feedback_fresh, sphere_gap, fit_line, mse
from algorithm_lab import jacobian, numerical_ik, astar, trapezoid, kalman_step, pid_demo
plt.rcParams.update({"figure.figsize": (7, 4), "axes.grid": True})
print("Python:", sys.executable)
print("Course:", ROOT.name)
'''


def cell(kind, source, index):
    value = {"id": f"cell-{index:03d}", "cell_type": kind, "metadata": {},
             "source": source.strip() + "\n"}
    if kind == "code":
        value.update(execution_count=None, outputs=[])
    return value


def build(path):
    chunks = re.split(r"^# %%([^\n]*)\n", path.read_text(encoding="utf-8"), flags=re.M)
    cells = []
    for index in range(1, len(chunks), 2):
        kind = "markdown" if "[markdown]" in chunks[index] else "code"
        source = chunks[index + 1]
        if kind == "markdown":
            source = "\n".join(line[2:] if line.startswith("# ") else line[1:] if line.startswith("#") else line
                               for line in source.splitlines())
        cells.append(cell(kind, source, len(cells)))
        if len(cells) == 1:
            cells.append(cell("code", SETUP, len(cells)))
    result = {"cells": cells, "metadata": {
        "kernelspec": {"display_name": "Training Python", "language": "python", "name": "training-python"},
        "language_info": {"name": "python", "version": "3.10"}}, "nbformat": 4, "nbformat_minor": 5}
    output = ROOT / "notebooks" / (path.stem + ".ipynb")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return output, len(cells)


if __name__ == "__main__":
    for path in sorted((ROOT / "notebooks" / "source").glob("*.py")):
        output, count = build(path)
        print(output.name, count, "cells")
