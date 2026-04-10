# Given a log file with timestamp ip method endpoint status response_time, 
# return the top 5 IP addresses by request count

import re
from collections import Counter

logfilepath = "sre-coding/log.log"

ipregx = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
ip_counter = Counter()

with open(logfilepath,"r") as f:
    for line in f:
        line.strip().split()
        print(line.strip().split())

        ips = ipregx.findall(line)
        if not ips:
            continue
        ips =ips[0]
        ip_counter[ips] += 1

    top5_ips = ip_counter.most_common(5)

    for ip, count in top5_ips:
        print(f"{ip}: {count} requests")