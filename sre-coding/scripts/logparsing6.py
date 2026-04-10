# Problem:
# Given a log file where each line contains:
#   ip  method  endpoint  status  response_time
#
# Task:
#   Find all IPs that have 3 or more CONSECUTIVE 5xx status codes
#   Order of lines in the file = order of requests
#
from collections import defaultdict

def logparser6(filepath: str) -> list[str]:
    streak      = defaultdict(int)
    result      = set()
    ip_counts   = defaultdict(int)   # track total requests per ip

    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) < 2:
                    continue

                ip     = parts[0]
                status = None

                # scan all parts — find first valid HTTP status code
                for part in parts[1:]:
                    try:
                        code = int(part)
                        if 100 <= code <= 599:
                            status = code
                            break
                    except ValueError:
                        continue

                if status is None:
                    continue

                ip_counts[ip] += 1    # count every request per ip

                if 500 <= status < 600:
                    streak[ip] += 1
                    if streak[ip] >= 3:
                        result.add(ip)
                else:
                    streak[ip] = 0

    except FileNotFoundError:
        print(f"[Error] File not found: {filepath}")
        return []

    # print ips with 3+ consecutive 5xx and their total request count
    print("\nIPs with 3+ consecutive 5xx errors:")
    for ip in sorted(result):
        print(f"  {ip:<20} total requests: {ip_counts[ip]}")

    return sorted(result)


logparser6("consectiveips.log")