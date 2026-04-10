# Given a log file with timestamp ip method endpoint status response_time, 
# return the top 5 IP addresses by request count

import re
from collections import Counter

IP_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

def top_ips(filepath: str, n :int = 5) -> list[tuple[str,int]]:
    ip_counter = Counter()

    with open(filepath,"r") as f:
        for line in f:
            try :
                ips =IP_pattern.findall(line)
                if not ips:
                    continue
                ip_counter[ips[0]] +=1
            except Exception:
                continue
    return ip_counter.most_common(n)

if __name__ == "__main__":
    results = top_ips("log.log")
    for ips, count in results:
        print(f"{ips}: {count} requests")
# 
# def top_ips_when_structured(filepath: str, n: int = 5) -> list[tuple[str, int]]:
#     ip_counter = Counter()
# 
#     try:
#         with open(filepath, "r") as f:
#             for line in f:
#                 line = line.strip()
# 
#                 # Guard 1 — skip empty lines
#                 if not line:
#                     continue
# 
#                 parts = line.split()
# 
#                 # Guard 2 — must have enough fields
#                 if len(parts) < 6:
#                     continue
# 
#                 ip = parts[1]   # IP always at index 1 — structure is known
# 
#                 # Guard 3 — basic sanity check instead of regex
#                 if "." not in ip:
#                     continue
# 
#                 ip_counter[ip] += 1
# 
#     except FileNotFoundError:
#         print(f"[Error] File not found: {filepath}")
#         return []
# 
#     return ip_counter.most_common(n)
# 
# 
# if __name__ == "__main__":
#     results = top_ips_when_structured("log.log")
#     for ip, count in results:
#         print(f"  {ip:<20} {count} requests")  