# def method():
#     count = 0
#     with open("access.log", "r", encoding="utf-8") as file:
#         for i in file:
#             count +=1
#     return count

def method_count_fast(filepath: str)-> int:
    count = 0
    last_byte = b""
    with open(filepath, "rb") as file:
        while chunk:= file.read(1<<20):
            count+= chunk.count(b"\n")
            last_byte = chunk[-1:]
        if last_byte and last_byte != b"\n":
            count = count + 1
    return count

count = method_count_fast("/Users/praveenreddy/leetcode/sre-coding/access.log")
print(count)


