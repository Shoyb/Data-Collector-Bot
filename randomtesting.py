import requests
import json
url = "https://api.apileague.com/retrieve-random-meme"
response = requests.get(url)
print(response.json())  