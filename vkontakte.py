import requests
from settings import *

params = {
    "domain": "eugenia_alekseenko",
    "count": 10,
    "filter": "owner",
    "extended": 1,
    "fields": ','.join(VK_NEEDED_PROFILE_FIELDS)
}

friends = requests.get(f"https://api.vk.com/method/wall.get?v=5.52&access_token={VK_TOKEN}", params=params).json()
print(friends)
print(','.join(VK_NEEDED_PROFILE_FIELDS))
# def get_user_wall():
#
