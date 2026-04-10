
from collections import defaultdict

def compute_metrics(logs):
    data = defaultdict(lambda:{"total": 0, "count": 0})

    for i in logs:
        parts = i.split()

        if len(parts) < 3:
            continue
        endpoint = parts[1]
        
        try:
            latency = int(parts[2])
        except ValueError:
            continue

        data[endpoint]["total"] += latency
        data[endpoint]["count"] += 1

    result = {}
    for endpoint, j in data.items():
            result[endpoint] = {
                "total_req" : j["count"],
                "avg_resp_time" : round(j["total"]/ j["count"],2)
            }
    return result


logs_test = [
    "2024-01-01 /api/users 120",
    "2024-01-01 /api/users 80",
    "2024-01-01 /api/orders 200",
]

#Test
result = compute_metrics(logs_test)

for a, b in result.items():
     print(a,b)

    