from collections import defaultdict

def count_status_codes(logs):

    data = defaultdict(int)

    for i in logs:
        parts = i.split()

        if len(parts) < 3:
            continue
        try:
            status_code = int(parts[2])
        except ValueError:
            continue
        data[status_code] += 1

    return data



# Test
# Test
logs_test = [
    "2024-01-01 /api/users 200",
    "2024-01-01 /api/orders 200",
    "2024-01-01 /api/users 404",
    "2024-01-01 /api/orders 500",
    "2024-01-01 /api/users 200",
]

data = count_status_codes(logs_test)

for a , b in data.items():
    print(a,"->", b)