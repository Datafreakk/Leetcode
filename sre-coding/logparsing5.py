# Problem:
# Given a list of timestamp strings in format "YYYY-MM-DD HH:MM:SS"
#
# Task:
#   1. Group all timestamps by (date, hour)
#   2. Count total requests per hour window
#   3. Print results in chronological order
#
# Input:
#   timestamps = [
#       "2026-03-10 08:15:23",
#       "2026-03-10 08:45:12",
#       "2026-03-10 09:01:01",
#   ]
#
# Output:
#   2026-03-10 08:00  —  2 requests
#   2026-03-10 09:00  —  3 requests
#
# Constraints:
#   - Skip malformed timestamps — never crash
#   - Output must be sorted chronologically
#   - Minutes and seconds are ignored — group by hour only
#   from collections import defaultdict

from collections import defaultdict
from datetime import datetime

def logparser5(timestamps: list[str]) -> defaultdict:
    request_per_hr = defaultdict(int)

    for ts in timestamps:
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        key = (dt.date(), dt.hour)
        request_per_hr[key] += 1

    # unpack directly in for — no need for separate date, hour = key
    for date, hour in sorted(request_per_hr):
        print(f"{date} {hour:02d}:00  —  {request_per_hr[(date, hour)]} requests")

    return request_per_hr