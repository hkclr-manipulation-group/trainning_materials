"""Execute each shipped notebook in its own fresh kernel and keep evidence."""
import json
import os
from pathlib import Path
import time
import argparse

import nbformat
from nbclient import NotebookClient
from start_classroom import environment

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="Optional notebook filenames; otherwise check all")
    args = parser.parse_args()
    os.environ.update(environment())
    output = ROOT / "outputs" / "executed_notebooks"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    paths = sorted((ROOT / "notebooks").glob("*.ipynb"))
    if args.names:
        known = {p.name: p for p in paths}
        unknown = set(args.names) - known.keys()
        if unknown:
            parser.error("unknown notebooks: " + ", ".join(sorted(unknown)))
        paths = [known[name] for name in args.names]
    for path in paths:
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
    report_name = "report_selected.json" if args.names else "report.json"
    (output / report_name).write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
