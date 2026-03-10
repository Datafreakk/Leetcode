# Find the endpoint with the highest average response time  
# [
#  ("/users", 120),
#  ("/orders", 200),
#  ("/users", 150),
#  ("/products", 300),
#  ("/orders", 100)
# ]

def log_parser4(logs):
    totals ={}
    counts = {}

    for endpoint, response in logs:
        totals[endpoint] = totals.get(endpoint,0) + response
        counts[endpoint] = counts.get(endpoint,0) + 1

    max_avg = 0
    result = None

    for endpoint in totals:
        avg = totals[endpoint]/ counts[endpoint]
        if avg > max_avg:
            max_avg = avg
            result = endpoint
    return result
    
        
logs = [
    ("/users", 120),
    ("/orders", 200),
    ("/users", 150),
    ("/products", 300),
    ("/orders", 100)
]

print(log_parser4(logs))