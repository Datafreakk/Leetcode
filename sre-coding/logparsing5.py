from collections import defaultdict
from datetime import datetime

def logparser5(timestamps):

    request_per_hr = defaultdict(int)

    for i in timestamps:
        dt = datetime.strptime(i,"%Y-%m-%d %H:%M:%S")
        key = (dt.date(),dt.hour)
        request_per_hr[key] +=1

    for i in sorted(request_per_hr):
        date, hour = i 
        print(f"{date} {hour}: {request_per_hr[i]} requests")

# Tests
timestamps = [
        "2026-03-10 08:15:23",
        "2026-03-10 08:45:12",
        "2026-03-10 09:01:01",
        "2026-03-10 09:30:30",
        "2026-03-10 09:55:00"
    ]
logparser5(timestamps)
