import requests
import random
import string
import time

url = "https://api.voomly.com/spotlights/t41jwghho3/customers"

headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'authorization': 'Bearer 3r3EOeJyAPo4KlQlNg6F8Vr9YYGtYY6U4HvtIn5nmnhSGGqALkKx5Y8txKMgcxIlh7ArQPJ9yrhoy0fsShhQcfkYhfajfJzAvlWKSZ2Lou18WbX8CV9qmlgMVCBO8lxe',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'origin': 'https://app.voomly.com',
    'funnel-version': '2',
    'player-version': '2'
}

def generate_random_email(name):
    clean_name = name.lower().replace(" ", "")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{clean_name}.{random_str}@example.test"

# Danh sách học viên mẫu
customers_to_add = [
    "Nguyen Khoa Phat",
    "Le Hoai Thu",
    "Tran Khanh Vy",
    "Pham Duc Anh",
    "Hoang Tuan Minh"
]

print("Bắt đầu tiến trình thêm học viên...")

for name in customers_to_add:
    email = generate_random_email(name)
    payload = {
        "name": name,
        "email": email,
        "password": "123456",
        "amount": 12300,
        "currency": "usd",
        "comment": "Tạo tự động bằng script"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Đã gọi API cho {name} ({email}) - Status Code: {response.status_code}")
        if response.status_code not in [200, 201]:
             print(f" Lỗi chi tiết: {response.text}")
    except Exception as e:
        print(f"Không thể kết nối cho {name}: {e}")
    
    # Tạm dừng 1 giây để tránh bị rate limit
    time.sleep(1)

print("Hoàn tất thêm học viên.")
