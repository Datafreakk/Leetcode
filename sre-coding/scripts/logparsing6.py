def logparser6(logs):
    
    from collections import defaultdict

    dic = defaultdict(int)
    result = set()
    for ip,status in logs:
        if 500 <= status < 600: 
            dic[ip] += 1
            if dic[ip] >= 3:
                result.add(ip)
        else:
            dic[ip] = 0
    print(result)      

logs = [
    ("192.168.1.1", 500),
    ("192.168.1.1", 502),
    ("192.168.1.1", 503),
    ("192.168.1.2", 200),
    ("192.168.1.1", 500),
    ("192.168.1.1", 200),
    ("192.168.1.2", 500),
    ("192.168.1.2", 501),
    ("192.168.1.2", 502)
]
logparser6(logs)


        
