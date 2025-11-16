from pathlib import Path

def normalize(path: Path) -> None:
    text = path.read_text()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("from __future__ import annotations"):
            break
    else:
        raise SystemExit("future import missing")

    docstring = "\n".join(lines[:i]).strip()
    rest = "\n".join(lines[i + 1 :])
    new_text = (
        "from __future__ import annotations\n\n"
        + (docstring + "\n\n" if docstring else "")
        + rest.lstrip()
        + "\n"
    )
    path.write_text(new_text)


if __name__ == "__main__":
    base = Path("C:/Hermes/agents")
    for module in ("historical.py", "technical.py"):
        normalize(base / module)

