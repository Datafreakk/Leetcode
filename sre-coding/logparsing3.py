# Question:Compute the percentage of requests with HTTP status ≥ 500 from a log file.

def log_parser(log:str) -> None:
    total_req = 0
    error_req = 0
    percent_of_error_req = 0
    
    try:
     with open(log, "r") as file:
         for line in file:
             lines = line.strip().split()
             if len(lines) < 9:
                 continue
             try:
                 status_code = int(lines[-2])
             except ValueError:
                 continue
             total_req +=1
             if status_code >=500:
                 error_req +=1
                                 
    except FileNotFoundError:
        print(f"[ERROR] Log file not found: {log}")
        return 
    if total_req == 0:
        print(f"[Warn] No valid Log entries found")
        return
    percent_of_error_req = (error_req/ total_req ) * 100 
    print(f"Total requests is: {total_req}")
    print(f"Total error requests is: {error_req}")
    print(f"Total percentage of error request is:  {percent_of_error_req:.2f}%")



log_parser("access.log")