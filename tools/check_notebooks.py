"""Execute each shipped notebook in its own fresh kernel and keep evidence."""
import json
import os
from pathlib import Path
import time

import nbformat
from nbclient import NotebookClient
from start_classroom import environment

ROOT = Path(__file__).resolve().parents[1]


def main():
    os.environ.update(environment())
    output = ROOT / "outputs" / "executed_notebooks"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        start = time.monotonic()
        client = NotebookClient(nb, timeout=120, kernel_name="training-python",
                                resources={"metadata": {"path": str(path.parent)}})
        client.execute()
        nbformat.write(nb, output / path.name)
        count = sum(c.cell_type == "code" for c in nb.cells)
        results.append({"notebook": path.name, "code_cells": count,
                        "seconds": round(time.monotonic() - start, 2), "status": "passed"})
        print(path.name, count, "code cells passed", flush=True)
    (output / "report.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
