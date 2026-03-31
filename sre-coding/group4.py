# Compute 95th percentile of response time per endpoint.

from collections import defaultdict
import math 

def p95_latency(logs):
    data = defaultdict(list)
    for i in logs:
      parts = i.split()
      if len(parts)< 3:
         continue
      
      endpoint = parts[1]
      try:
         latency = int(parts[2])
      except ValueError:
        continue
         

      data[endpoint].append(latency)
      
    result = {}

    for endpoint, latency in data.items():
       latency.sort()
       n = len(latency)
       index = math.ceil(0.95 * n)- 1
       result[endpoint] = latency[index]
    return result 

logs = [
    "10:00 /api 100",
    "10:01 /api 200",
    "10:02 /api 300",
    "10:03 /api 400",
    "10:04 /api 500"
]

print(p95_latency(logs))


