import heapq
from collections import Counter

def top_k_ips(fileapth:str , k: int) -> list[tuple[str,int]]:
    ip_count = Counter()
    with open(fileapth, "r") as file:
        for i in file:
            parts = i.strip().split()
            if len(parts)< 3:
                continue
            ip = parts[0]
            ip_count[ip] +=1
    return heapq.nlargest(k,ip_count.items(),lambda x: x[1])

results = top_k_ips("/Users/praveenreddy/leetcode/sre-coding/access.log", 2)
for ip,count in results:
    print(f"{ip} {count}")
