# que:ompute the percentage of requests with HTTP status ≥ 500 from a log file.

def logparser3(log):
    tot_requests = 0
    error_requests = 0

    with open ("access.log", "r" ) as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) < 2:
                continue

            try:
             statuscode = int(parts[-2])
            except ValueError:
                continue

            tot_requests +=1
            if statuscode > 500:
                error_requests += 1
            
    if tot_requests == 0:
        error_requests = 0
    else:
        total_percenatge = (error_requests/tot_requests ) * 100

    print(f"Total requests: {tot_requests}")
    print(f"5xx requests: {error_requests}")
    print(f"Percentage: {total_percenatge:.2f}%")


logparser3("access.log")
