import requests
import json
url = "https://api.animechan.io/v1/quotes/random"
response = requests.get(url)
data = response.json()
print(data)