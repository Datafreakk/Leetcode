import random
from datetime import datetime, timedelta

VALID_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
STATUS_CODES = ["200", "201", "400", "401", "403", "404", "500", "502"]
URLS = ["/api/login", "/api/orders", "/api/products", "/api/users", "/api/cart"]

# Approximate line size: ~100 bytes
TARGET_SIZE_GB = 1
TARGET_SIZE_BYTES = TARGET_SIZE_GB * 1024 * 1024 * 1024
CURRENT_SIZE = 0

start_time = datetime(2026, 3, 13, 0, 0, 0)
time_delta = timedelta(seconds=1)

with open("accesslog_1GB.log", "w") as f:
    while CURRENT_SIZE < TARGET_SIZE_BYTES:
        ts = start_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
        ip = f"{random.randint(1, 255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        method = random.choice(VALID_METHODS)
        url = random.choice(URLS)
        status = random.choice(STATUS_CODES)
        latency = random.randint(10, 1000)

        line = f'{ip} - - [{ts}] "{method} {url} HTTP/1.1" {status} {latency}\n'
        f.write(line)
        CURRENT_SIZE += len(line)

        start_time += time_delta