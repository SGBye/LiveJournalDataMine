import time
from pprint import pprint

import requests
from settings import *

# params = {
#     "owner_id": "2963979",
#     "count": 10,
#     "filter": "owner",
#     "extended": 1,
#     "fields": ','.join(VK_NEEDED_PROFILE_FIELDS)
# }
#
# friends = requests.get(f"https://api.vk.com/method/wall.get?v=5.52&access_token={VK_TOKEN}", params=params).json()
#
# for i in friends['response']['items']:
#     print(i['text'])
# # pprint(friends)
# # def get_user_wall():
# #
# params = {
#     "group_id": "tvoicomicsi",
#     "sort": "id_asc"
# }
# group_settings = requests.get(f"https://api.vk.com/method/groups.getMembers?v=5.52&access_token={VK_TOKEN}",
#                               params=params).json()
#
# pprint(len(group_settings['response']['items']))
from utils import batch


class VKApi:
    BASE_URL = "https://api.vk.com/method"
    API_VERSION = "5.9"

    def __init__(self, vk_token):
        self.vk_token = vk_token

    def get_group_members(self, group_id, total_count, offset=0, fields=None):
        method = 'groups.getMembers'
        params = {
            "group_id": group_id,
            "sort": "id_asc",
        }

        if fields is not None:
            params['fields'] = ','.join(fields)

        # max batch size = 1000 on VK side
        needed_iterations = total_count // 1000
        flat_amount = total_count % 1000
        ids = []

        for i in range(needed_iterations):
            params['offset'] = offset + (i * 1000)
            pack = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={self.vk_token}",
                                params=params).json()['response']['items']
            ids.extend(pack)

        if flat_amount:
            if not params.get('offset'):
                params['offset'] = 0
            else:
                params['offset'] += 1000

            params['count'] = flat_amount
            last_batch = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={self.vk_token}",
                                      params=params).json()

            ids.extend(last_batch)

        return ids

    def get_user_token(self):
        return requests.get(
            "https://oauth.vk.com/authorize?client_id=7164317&display=page&response_type=token&v=5.103&state=123456")

    def search(self, filter_params, user_token):
        method = 'users.search'

        allowed_query_params = ['city', 'country', 'age_from', 'age_to', 'fields', 'count', 'sex',
                                'birth_day', 'birth_month', 'birth_year', 'group_id', 'sort']
        for i in filter_params.keys():
            if i not in allowed_query_params:
                print(i)
        assert all(i in allowed_query_params for i in filter_params.keys())

        users = requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={user_token}",
                             params=filter_params).json()

        return users['response']['items']

    def get_users_messages(self, ids, token):
        method = "execute"
        response = []
        full = len(ids) // 25
        count = 1
        for pack in batch(list(ids), 25):
            print(f"***Batch {count} out of {full}...")
            length = len(pack)
            vk_code = f"""
            var response = [];
            var ids = {pack};
            var count = 0;
            while (count != {length - 1}) {{
                response.push( {{"id": ids[count], "messages": API.wall.get( {{"owner_id": ids[count], "count": 10, "filter": "owner"}} ) }});
                count = count + 1;
            }}
            return response;
            """
            try:
                response.extend(requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={token}",
                                             params={"code": vk_code}).json()['response'])
            except KeyError:
                print(requests.get(f"{self.BASE_URL}/{method}?v={self.API_VERSION}&access_token={token}",
                                                 params={"code": vk_code}).json())
            time.sleep(3)
            count += 1
        return response
