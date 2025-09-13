import requests

coins = requests.get("https://api.coingecko.com/api/v3/coins/list").json()
for c in coins:
    if "ondo" in c['id'] or "illuvium" in c['id']:
        print(c)
