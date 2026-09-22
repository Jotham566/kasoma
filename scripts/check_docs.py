"""Validate local Markdown file links and SRD implementation-register coverage."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def main():
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    ).decode().split("\0")
    errors = []
    checked = 0
    for name in sorted(set(names)):
        path = ROOT / name
        if path.suffix != ".md" or not path.is_file():
            continue
        checked += 1
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            link = urlsplit(target.strip("<>"))
            if link.scheme or link.netloc or not link.path:
                continue
            if not (path.parent / unquote(link.path)).exists():
                errors.append(f"{name}: missing link target {target}")

    srd = (ROOT / "docs/specifications/01_SRD.md").read_text()
    register = (ROOT / "docs/implementation/REQUIREMENTS_TRACEABILITY.md").read_text()
    pattern = r"^\| ((?:FR|NFR)-[A-Z]+-\d+) \|"
    expected = set(re.findall(pattern, srd, re.MULTILINE))
    actual = re.findall(pattern, register, re.MULTILINE)
    if not expected or set(actual) != expected or len(actual) != len(set(actual)):
        errors.append("Traceability must contain every SRD requirement exactly once.")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Checked links in {checked} Markdown files and coverage of {len(expected)} requirements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
