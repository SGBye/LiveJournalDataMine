import requests
from settings import *

friends = requests.get(f"https://api.vk.com/method/friends.getOnline?v=5.52&access_token={VK_TOKEN}").json()
print(friends)
sspankratov