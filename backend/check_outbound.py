import requests

response = requests.get('http://localhost:5000/api/stock-outs')
print(f'状态码: {response.status_code}')
data = response.json()
print(f'出库记录数量: {len(data.get("data", []))}')
for record in data.get('data', []):
    print(f'- {record["name"]}: {record["quantity"]}{record["unit"]} ({record["out_time"]})')