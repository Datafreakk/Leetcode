from urllib.parse  import urlparse

logs = [
    "GET https://example.com/api/users 200",
    "POST http://sub.domain.org/login 302",
    "GET https://www.google.com/search?q=test 200"
]

def extract_url_log(log_lines):
    for log in log_lines.split():
        if log.startswith("https://") or log.startswith("http://"):
            parsed = urlparse(log)
            return f"{parsed.scheme}://{parsed.netloc}"
    return None
    
extarcter =  [extract_url_log(i) for i in logs]

print(extarcter)