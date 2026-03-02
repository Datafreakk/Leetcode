from datetime import datetime
from typing import Optional
import re

def logparser(log:str) -> Optional[dict]:
    log = log.strip()
    if not log:
        return None

    try: 

            # 2026-03-01T10:00:00Z INFO auth-service User login success id=123 latency=120ms

            match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(\w+)\s+(\S+)", log)
            
            if not match:
                return None
            tsr, level, service = match.groups()
            timestamp = datetime.strptime(tsr,"%Y-%m-%dT%H:%M:%SZ")


            user_id = None 
            latency_ms = None

            for part in log.split():
                if part.startswith("id="):
                    user_id = int(part.split("=")[1])
                elif part.startswith("latency="):
                    latency_ms = int(part.split("=")[1].replace("ms",""))
           
            if user_id is None:
                return None

            return {
                "timestamp" : timestamp,
                "level" : level,
                "service":   service,
                "user_id":   user_id,
                "latency_ms": latency_ms
               }



    except Exception:
       return None
    

# --- Test ---
lines = [
    "2026-03-01T10:00:00Z INFO auth-service User login success id=123 latency=120ms",
    "2026-03-01T10:01:00Z ERROR auth-service Login failed id=456",           # missing latency
    "  2026-03-01T10:02:00Z  WARNING  auth-service  Retry id=789 latency=300ms  ", # extra spaces
    "2026-03-01T10:03:00Z INFO auth-service Something happened",             # missing id
    "%%% corrupted log line @@@",                                            # garbled
    "",                                                                       # empty
]

for line in lines:
    print(logparser(line))
