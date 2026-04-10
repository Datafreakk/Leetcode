# SRE Scripting — Practice Problems

> 18 problems covering log parsing, string manipulation, file handling, and aggregation patterns commonly asked in SRE coding rounds.

---

## 📊 Full Inventory — 18 Problems

### Log Parsing (8)

| # | Problem | File | Core Skill |
|---|---------|------|------------|
| 1 | Structured key=value log → typed dict | `logparsing1.py` | regex, datetime, validation |
| 2 | Top N IPs by count | `logparsing2.py` | regex, Counter |
| 3 | 5xx error rate % | `logparsing3.py` | field splitting, math |
| 4 | Slowest endpoint (multi-format CLF) | `logparsing4.py` | multi-format parsing, averages |
| 5 | Group requests by hour | `logparsing5.py` | datetime bucketing |
| 6 | IPs with 3+ consecutive 5xx | `logparsing6.py` | stateful streak tracking |
| 7 | JSON log parsing + error signatures | `logparsing7.py` | json.loads, JSONDecodeError, composite grouping |
| 8 | Multi-key aggregation (service × hour) | `logparsing8.py` | tuple keys, multi-level sort |

### Strings (3)

| # | Problem | File | Core Skill |
|---|---------|------|------------|
| 9 | Extract URLs from log lines | `strings.py` | urlparse |
| 10 | Normalize multiple timestamp formats | `strings2.py` | datetime.strptime, multi-format |
| 11 | Count HTTP methods from CLF | `strings3.py` | quoted-string splitting |

### File Handling (3)

| # | Problem | File | Core Skill |
|---|---------|------|------------|
| 12 | Fast line count (binary chunked reads) | `filehandling1.py` | binary I/O, `1<<20` chunks |
| 13 | Top K IPs with heapq | `filehandling2.py` | heapq.nlargest |
| 14 | Append to log file | `filehandling3.py` | basic file write |

### GroupBy / Aggregation (4)

| # | Problem | File | Core Skill |
|---|---------|------|------------|
| 15 | Avg response time per endpoint | `groupby1.py` | defaultdict, aggregation |
| 16 | Count status codes | `groupby2.py` | defaultdict(int) |
| 17 | Top 5 active users | `groupby3.py` | sorted + slice |
| 18 | P95 latency per endpoint | `group4.py` | percentile math |

---

## 🧰 Key Python Constructs Covered

- `re.compile()`, `re.findall()`, `re.match()`
- `collections.Counter`, `collections.defaultdict`
- `datetime.strptime()`, `datetime.strftime()`
- `json.loads()`, `json.JSONDecodeError`
- `heapq.nlargest()`
- `urllib.parse.urlparse()`
- Binary file I/O (`open("rb")`, chunked reads)
- `sorted()` with `key=lambda`, multi-level sorting
- Defensive parsing — skip malformed lines, never crash

---


