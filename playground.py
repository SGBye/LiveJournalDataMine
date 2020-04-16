from datetime import date

from models import User, Message
from settings import VK_TOKEN
from vkontakte import VKApi

vk_api = VKApi(VK_TOKEN)
group_name = "ria"
vk_link_pattern = "https://vk.com/id{user_id}?w=wall{user_id}_{message_id}%2Fall"
# ids = vk_api.get_group_members(group_name, 5000, fields=['bdate,city'])
# print(len(ids))

# ria_male = vk_api.search({
#     'group_id': 15755094,  # ria news
#     'sex': 2,
#     'fields': 'bdate,sex,interests,domain,city,country',
#     'count': 1000
# }, '92b735f78f5ca774c2c2c8ac478f6fe06a4fa1fb17b883f9c73ae9626311cbc6a67b6810e1bcd370660b9')
#
# for user in ria_male:
#     try:
#         User.create(nick=user.get('domain', user['id']), birthdate=user.get('bdate'),
#                 interests=user.get('interests'), source='vkontakte', sex='male',
#                 city=user.get('city'), country=user.get('country'))
#     except:
#         continue
#
# male_ids = set()
# for i in ria_male:
#     male_ids.add(i['id'])
#
# male_messages = []
# a = vk_api.get_users_messages(male_ids, '92b735f78f5ca774c2c2c8ac478f6fe06a4fa1fb17b883f9c73ae9626311cbc6a67b6810e1bcd370660b9')
# with open('male.txt', 'w', encoding='utf8') as f:
#     for i in a:
#         if isinstance(i['messages'], dict):
#             for b in i['messages']['items']:
#                 try:
#                     Message.create(link=vk_link_pattern.format(user_id=i['id'], message_id=b['id']),
#                                message=b['text'].split('\n'),
#                                author=int(i['id']),
#                                date=date.fromtimestamp(b['date']))
#                 except:
#                     continue
#                 f.write(' '.join(b['text'].split('\n')) + '\n')

# ria_female = vk_api.search({
#     'sex': 1,
#     'group_id': 15755094,  # ria news
#     'fields': 'bdate,sex,interests,domain,city,country',
#     'count': 1000
# }, '92b735f78f5ca774c2c2c8ac478f6fe06a4fa1fb17b883f9c73ae9626311cbc6a67b6810e1bcd370660b9')
#
# for user in ria_female:
#     try:
#         User.create(nick=user.get('domain', user['id']), birthdate=user.get('bdate'),
#                     interests=user.get('interests'), source='vkontakte', sex='female',
#                     city=user.get('city'), country=user.get('country'))
#     except:
#         continue
#
# female_ids = set()
# for i in ria_female:
#     female_ids.add(i['id'])
#
# c = vk_api.get_users_messages(female_ids,
#                               '92b735f78f5ca774c2c2c8ac478f6fe06a4fa1fb17b883f9c73ae9626311cbc6a67b6810e1bcd370660b9')
# with open('above_18.txt', 'w', encoding='utf8') as f:
#     for i in c:
#         if isinstance(i['messages'], dict):
#             for b in i['messages']['items']:
#                 Message.create(link=vk_link_pattern.format(user_id=i['id'], message_id=b['id']),
#                                message=b['text'].split('\n'),
#                                author=int(i['id']),
#                                date=date.fromtimestamp(b['date']))
#                 f.write(' '.join(b['text'].split('\n')) + '\n')
male = User.filter(sex='male')
nicks = [user.nick for user in male if not user.nick.startswith('id')]
ids = [int(user.nick.replace('id', '')) for user in male if user.nick.startswith('id')]
print()