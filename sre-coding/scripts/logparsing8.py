# Problem: Multi-Key Aggregation — Error Count per Service per Hour
#
# Context:
#   You're on-call and need to quickly identify which service started
#   throwing errors and during which hour — essentially a pivot table
#   of (service, hour) → error count from your access logs.
#
# Sample input (log file, one line per request):
#
#   2026-04-10T08:15:01Z  ERROR  payment-svc   POST /charge       500  320ms
#   2026-04-10T08:45:30Z  ERROR  payment-svc   POST /charge       502  150ms
#   2026-04-10T08:50:00Z  INFO   auth-svc      GET  /health       200  10ms
#   2026-04-10T09:01:12Z  ERROR  payment-svc   POST /charge       500  450ms
#   2026-04-10T09:15:00Z  ERROR  auth-svc      POST /login        503  2000ms
#   2026-04-10T09:20:00Z  WARN   order-svc     GET  /orders       200  80ms
#   2026-04-10T10:00:00Z  ERROR  auth-svc      POST /login        500  3500ms
#   2026-04-10T10:05:00Z  ERROR  auth-svc      POST /login        503  4200ms
#
# Task:
#   1. Read the log file line by line
#   2. Parse each line to extract: timestamp, level, service
#   3. Skip lines that are malformed or missing fields — never crash
#   4. Filter only ERROR-level entries
#   5. Group by (service, hour) — hour derived from timestamp as "YYYY-MM-DD HH:00"
#   6. Count errors per (service, hour) bucket
#   7. Print results sorted by:
#      - service name (ascending), then
#      - hour (chronological)
#
# Expected output for the sample above:
#
#   Service              Hour              Errors
#   ─────────────────────────────────────────────
#   auth-svc             2026-04-10 09:00       1
#   auth-svc             2026-04-10 10:00       2
#   payment-svc          2026-04-10 08:00       2
#   payment-svc          2026-04-10 09:00       1
#
# Bonus (if time permits):
#   - Also compute total requests (all levels) per (service, hour)
#     and report error_rate = errors / total * 100 for each bucket
#   - Flag any bucket where error_rate > 50% as "⚠ HIGH"
#
# Constraints:
#   - File may not exist — handle FileNotFoundError
#   - File may be empty — return empty result
#   - Timestamp format is fixed: ISO 8601 "YYYY-MM-DDTHH:MM:SSZ"
#   - Log level is always the 2nd field
#   - Service name is always the 3rd field
#
# Skills tested:
#   datetime.strptime(), tuple keys in defaultdict, multi-key grouping,
#   sorted() with multi-level key, conditional filtering, tabular output
