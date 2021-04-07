import requests

response = requests.get("https://www.okex.com/api/spot/v3/instruments/OKB-USDT/ticker"
#                         , proxies={
#     'http': 'http://127.0.0.1:10808',
#     'https': 'http://127.0.0.1:10808'
# }
                        )

print(response.text)