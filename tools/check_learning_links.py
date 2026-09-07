"""Check local Markdown links in course documents and notebook prose."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "outputs", "__pycache__", ".ipynb_checkpoints"}


def main():
    errors, counts = [], {"markdown": 0, "notebooks": 0, "local_links": 0}
    for path in ROOT.rglob("*"):
        if SKIP.intersection(path.relative_to(ROOT).parts):
            continue
        if path.suffix == ".md":
            source = path.read_text(encoding="utf-8")
            counts["markdown"] += 1
        elif path.suffix == ".ipynb":
            nb = json.loads(path.read_text(encoding="utf-8"))
            source = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
            counts["notebooks"] += 1
        else:
            continue
        for target in re.findall(r"\]\(([^\n)]+)\)", source):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            counts["local_links"] += 1
            if not (path.parent / unquote(parsed.path)).exists():
                errors.append(f"{path.relative_to(ROOT)} -> {target}")
    for error in errors:
        print(error)
    print(counts, "broken:", len(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
