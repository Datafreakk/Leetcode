import sys
from collections import defaultdict

VALID_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}


# def http_method_counter(filename):
#     method_counts = defaultdict(int)
    
    # with open(filename, 'r') as file:
    #     for i in file:
    #         try:
    #             part = i.split('"')
    #             if len(part) < 2:
    #                 continue
    #             request_part  = part[1]
    #             method_name = request_part.split()[0]
    #             method_counts[method_name] += 1
    #         except(IndexError,ValueError) as e:
    #             continue
    #         # print(method_counts.items())
    # return method_counts
def count_http_methods_stream():
    method_counts = defaultdict(int)
    for i in sys.stdin:
        try:
            parts = i.split('"')
            if len(parts) < 2:
                continue
            method_part = parts[1]
            method_name = method_part.split()[0]
            if method_name in VALID_METHODS:
                method_counts[method_name] += 1
        except(IndexError, ValueError):
            continue
    return method_counts
            
                           

if __name__ == "__main__":
    # counts = http_method_counter("accessloge.log")
    counts = count_http_methods_stream()
    
    for method, count in sorted(counts.items()):
        print(f"{method}: {count}")
    
            
        