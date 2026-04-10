import re
from datetime import datetime
from typing import Optional

LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(\w+)\s+(\S+)"
)

def logparser(log: str) -> Optional[dict]:
    """Parse a single log line string — returns dict or None."""
    log = log.strip()
    if not log:
        return None

    try:
        match = LOG_PATTERN.match(log)
        if not match:
            return None

        tsr, level, service = match.groups()
        timestamp = datetime.strptime(tsr, "%Y-%m-%dT%H:%M:%SZ")

        user_id    = None
        latency_ms = None

        for part in log.split():
            if part.startswith("id="):
                try:
                    user_id = int(part.split("=")[1])
                except ValueError:
                    return None
            elif part.startswith("latency="):
                try:
                    latency_ms = int(part.split("=")[1].replace("ms", ""))
                except ValueError:
                    latency_ms = None

        if user_id is None:
            return None

        return {
            "timestamp":  timestamp,
            "level":      level,
            "service":    service,
            "user_id":    user_id,
            "latency_ms": latency_ms,
        }

    except Exception:
        return None


def parse_log_file(filepath: str) -> list[dict]:
    """Read a log file and return parsed records — skips bad lines."""
    results = []

    with open(filepath, "r") as f:
        for line in f:
            result = logparser(line)
            if result:
                results.append(result)

    return results


if __name__ == "__main__":
    records = parse_log_file("sre-coding/log.log")

    for record in records:
        print(record)