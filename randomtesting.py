import requests

response = requests.get(
    "https://api.waifu.im/images",
    params={"IncludedTags": "waifu"}
)
data = response.json()
print(data["items"][0]["url"])