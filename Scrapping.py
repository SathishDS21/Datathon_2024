# pip install zenrows
from zenrows import ZenRowsClient

client = ZenRowsClient("ee5e305a575bb3c45664a84d5ab6d49a388bfb44")
url = "https://www.reuters.com/markets/europe/markets-jury-still-out-french-belt-tightening-plan-2024-10-11/"

response = client.get(url)

print(response.text)