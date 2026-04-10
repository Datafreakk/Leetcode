# Problem:
# Given a log file in either:
#   Format 1 (quoted CLF): 127.0.0.1 - - [date] "GET /users HTTP/1.1" 200 120
#   Format 2 (no quotes):  127.0.0.1 - - [date] GET /users HTTP/1.1 200 120
#
# Task:
#   1. Parse each line and extract endpoint + response time
#   2. Handle BOTH log formats — quoted and unquoted
#   3. Accumulate total response time and request count per endpoint
#   4. Compute average response time per endpoint
#   5. Return the endpoint with the HIGHEST average response time
#   6. Skip malformed lines silently — never crash
#
# Input:
#   filepath — path to the log file
#
# Output:
#   (endpoint, avg_response_time)
#   e.g. ('/products', 275.0)
#
# Constraints:
#   - response time field may be "-" or non-numeric — skip that line
#   - endpoint must start with "/" — skip if not
#   - file may not exist — handle FileNotFoundError
#   - file may be empty or have no valid lines — handle gracefully

from collections import defaultdict

def log_parser4(log: str) -> None:
    counts = defaultdict(int)
    totals = defaultdict(float)

    try:
        with open(log, "r") as file:
            for line in file:
                lines = line.strip()

                if not lines:
                    continue

                # Strategy 1 — quoted format (standard CLF)
                # '127.0.0.1 - - [date] "GET /users HTTP/1.1" 200 120'
                if '"' in lines:
                    parts = lines.split('"')
                    if len(parts) < 3:
                        continue

                    request_part  = parts[1].split()   # ['GET', '/users', 'HTTP/1.1']
                    response_part = parts[2].split()   # ['200', '120']

                # Strategy 2 — no quotes, plain space split
                # '127.0.0.1 - - [date] GET /users HTTP/1.1 200 120'
                else:
                    parts = lines.split()
                    if len(parts) < 9:
                        continue

                    request_part  = parts[5:8]    # ['GET', '/users', 'HTTP/1.1']
                    response_part = parts[8:]     # ['200', '120']

                # shared logic — same for both strategies
                if len(request_part) < 2 or len(response_part) < 1:
                    continue

                endpoint = request_part[1]        # '/users'

                if not endpoint.startswith("/"):
                    continue

                try:
                    response = float(response_part[-1])
                except ValueError:
                    continue

                totals[endpoint] += response
                counts[endpoint] += 1

    except FileNotFoundError:
        print(f"[Error] File not found: {log}")
        return None

    if not totals:
        print("[Warn] No valid entries found")
        return None

    max_avg = -1
    result  = None

    for endpoint in totals:
        avg = totals[endpoint] / counts[endpoint]
        print(f"  {endpoint:<20} requests: {counts[endpoint]}   avg: {avg:.2f}ms")
        if avg > max_avg:
            max_avg = avg
            result  = endpoint

    return result, round(max_avg, 2)


endpoint, avg = log_parser4("acc.log")
print(f"\nSlowest endpoint : {endpoint}")
print(f"Average response : {avg}ms")