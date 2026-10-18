"""Read-only comparison of supplied synthetic reports; no provider imports or calls."""

import json
import os
from pathlib import Path

from services.evaluation_reports import compare, read_report


def main() -> int:
    baseline = os.environ.get("KASOMA_EVAL_BASELINE")
    candidate = os.environ.get("KASOMA_EVAL_CANDIDATE")
    if not baseline or not candidate:
        print(json.dumps({"status": "FAILED", "code": "REPORT_PATHS_REQUIRED"}))
        return 1
    try:
        result = compare(read_report(Path(baseline)), read_report(Path(candidate)))
    except (ValueError, OSError, RecursionError):
        # Never echo file paths, validation inputs, exception messages or excerpts.
        print(json.dumps({"status": "FAILED", "code": "REPORT_COMPARISON_REJECTED"}))
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
