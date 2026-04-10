# Problem: JSON Log Parsing — Extract & Summarize Errors from Structured JSON Logs
#
# Context:
#   Your Kubernetes microservices emit JSON logs to stdout.
#   Each line is a JSON object, but some lines are malformed
#   (truncated, non-JSON, or missing required fields).
#
# Sample input (one JSON object per line):
#
#   {"timestamp": "2026-04-10T08:12:01Z", "level": "ERROR", "service": "payment-svc", "msg": "timeout connecting to db", "trace_id": "abc123", "latency_ms": 3200}
#   {"timestamp": "2026-04-10T08:12:02Z", "level": "INFO",  "service": "auth-svc",    "msg": "login success", "trace_id": "def456", "latency_ms": 45}
#   MALFORMED LINE — container runtime garbage
#   {"timestamp": "2026-04-10T08:12:03Z", "level": "ERROR", "service": "payment-svc", "msg": "timeout connecting to db", "trace_id": "ghi789", "latency_ms": 3500}
#   {"timestamp": "2026-04-10T08:12:04Z", "level": "WARN",  "service": "order-svc",   "msg": "slow query detected", "latency_ms": 800}
#   {"level": "ERROR", "service": "auth-svc"}
#
# Task:
#   1. Read the log file line by line
#   2. Parse each line as JSON using json.loads()
#   3. Skip any line that:
#      - is not valid JSON (handle json.JSONDecodeError)
#      - is missing any of the required fields: "timestamp", "level", "service", "msg"
#   4. Filter only ERROR-level entries
#   5. Group errors by (service, msg) — i.e. unique error signatures
#   6. For each unique error signature, report:
#      - count of occurrences
#      - average latency_ms (latency_ms may be missing — treat as None, exclude from avg)
#      - list of trace_ids (trace_id may be missing — skip those)
#   7. Return results sorted by count descending
#
# Expected output for the sample above:
#   {
#       ("payment-svc", "timeout connecting to db"): {
#           "count": 2,
#           "avg_latency_ms": 3350.0,
#           "trace_ids": ["abc123", "ghi789"]
#       }
#   }
#
# Constraints:
#   - Never crash on bad input — skip and continue
#   - File may not exist — handle FileNotFoundError
#   - File may be empty or have zero valid ERROR lines — return empty dict
#   - latency_ms and trace_id are optional fields
#
# Skills tested:
#   json.loads(), JSONDecodeError handling, dict.get(), defaultdict,
#   grouping by composite key, conditional aggregation, defensive parsing
