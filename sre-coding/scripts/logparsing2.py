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
        
        