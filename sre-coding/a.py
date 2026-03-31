with open("/Users/praveenreddy/leetcode/sre-coding/access.log", "rb") as f:
    content = f.read()
    print(repr(content))