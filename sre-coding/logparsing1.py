# Problem:
# Given a structured log file where each line contains:
#   timestamp (ISO format), log level, service name
#   and optional key=value pairs (id=, latency=)
#
# Task:
#   1. Parse each line into a typed dict
#   2. id= is mandatory — skip line if missing or not an integer
#   3. latency= is optional — None if missing
#   4. Skip malformed lines silently — never crash
#   5. Return only valid records as a list of dicts
#
# Input line:
#   2026-04-09T10:00:01Z  INFO  auth-service  id=101 latency=120ms
#
# Output dict:
#   {
#       "timestamp":  datetime object,
#       "level":      "INFO",
#       "service":    "auth-service",
#       "user_id":    101,
#       "latency_ms": 120
#   }


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