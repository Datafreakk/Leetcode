from collections import defaultdict

def top_active_users(logs):

    data = defaultdict(int)
    for i in logs:
        parts = i.split()

        if len(parts)< 3:
            continue
        user_id = parts[1]
        data[user_id] +=1

    sorted_users = sorted(data.items(), key = lambda x:x[1], reverse= True)
    Top_5 = sorted_users[:5]
    return Top_5 


# Test
logs_test = [
    "2024-01-01 user_1 /api/orders",
    "2024-01-01 user_2 /api/users",
    "2024-01-01 user_1 /api/users",
    "2024-01-01 user_3 /api/orders",
    "2024-01-01 user_2 /api/users",
    "2024-01-01 user_1 /api/orders",
    "2024-01-01 user_4 /api/users",
    "2024-01-01 user_5 /api/orders",
    "2024-01-01 user_6 /api/users",
    "2024-01-01 user_1 /api/orders",
]

result = top_active_users(logs_test)
for a,b in result:
    print(a,b)