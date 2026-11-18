#!/usr/bin/env python3
"""
Turn a serve.py request log (JSON lines) into one readable JSON file.

    python pretty_log.py                          newest logs/requests_*.jsonl
    python pretty_log.py logs/requests_X.jsonl    a specific log
    python pretty_log.py SRC.jsonl DST.json       choose the output file too

serve.py names each log for the moment the server started, like
logs/requests_2026-11-18_105410.jsonl. The start time is year-month-day then
hour-minute-second, so sorting the names puts the newest last.

The output is a JSON array of the records, indented. The original .jsonl is
left alone; it is the run record, and this file is a copy for reading.
"""

import json
import sys
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"


def newest_log() -> Path:
    """The most recent timestamped log, or the old fixed-name one."""
    logs = sorted(LOG_DIR.glob("requests_*.jsonl"))
    if logs:
        return logs[-1]
    fallback = LOG_DIR / "requests.jsonl"
    if fallback.exists():
        return fallback
    sys.exit(f"No request logs found in {LOG_DIR}. Run serve.py and send a request first.")


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_log()
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pretty.json")

    with open(src, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Read {len(records)} records from {src}")
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
