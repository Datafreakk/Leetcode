
# Dictionary

a = {"name":"praveen",1:"abc",3:"abv"}
# print(a.get("names","no luck"))

b = dict(name = "praveen", age = 22)
# print(b["age"])

c = {1: "one", "two": 2, (3, 4): "tuple key"}
print(c[(3, 4)])

for i in a:
    print(i,a[i] )

for k,v in a.items():
    print(k,v)


squares = { i : i*i for i in range(5)}
# print(squares.get("i"))

print(list(squares.items())) 
# [(0, 0), (1, 1), (2, 4), (3, 9), (4, 16)]

print(list(a.items()))

# d1.keys()      # returns dict_keys([...])
# d1.values()    # returns dict_values([...])
# d1.items()     # returns dict_items([...])
# d1.copy()      # shallow copy


# 1.Keys():Use when you need to check keys, iterate over keys, or convert keys to a list.
# 2.items: Returns a view of (key, value) pairs.
# 3..get(key, default)

for key,value in a.items():
    if value == "praveen":
        print(value)


# default dict:   subclass of dict that automatically provides a default value for missing keys instead of raising KeyError

from collections import defaultdict
d = defaultdict(int)
listt = defaultdict(list)
print(d)
print(listt)

words =["apple", "banana", "apple"]
count = defaultdict(int)

for i in words:
    count[i] +=1
print(dict(count))


# ietrate of over list and penned values to key 
group = defaultdict(list)
pairs = [("fruits", "apple"), ("fruits", "banana")]

for k, v in pairs:
    group[k].append(v)
print(dict(group))