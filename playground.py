import json
import re
from datetime import date

from models import User, Message
from settings import VK_TOKEN
from vkontakte import VKApi

ID_REGEX = re.compile(r"^id\d+$")

vk_api = VKApi(VK_TOKEN)
VK_USER_TOKEN = "bb313324e2d6d91e2e5aa9c3ed57715785058d6967a5801b06e942b9cf09bb45f5904e6fdb8555d334018"
group_name = "ria"
ria_news_id = 15755094
vk_music_id = 147845620
vk_link_pattern = "https://vk.com/id{user_id}?w=wall{user_id}_{message_id}%2Fall"


# ids = vk_api.get_group_members(group_name, 5000, fields=['bdate,city'])
# print(len(ids))

# ria_male = vk_api.search({
#     'group_id': 15755094,  # ria news
#     'sex': 2,
#     'fields': 'bdate,sex,interests,domain,city,country',
#     'count': 1000
# }, VK_USER_TOKEN)

def write_messages(users, filename):
    with open(filename, 'w', encoding='utf8') as f:
        for user in users:
            for message in user.messages:
                f.write(' '.join(message.message.split('\n')) + '\n')


def create_users_by_gender_and_group(sex, group_id):
    sex_id = 1 if sex == 'female' else 2

    ria_female = vk_api.search({
        'sex': sex_id,
        'sort': 1,
        'group_id': group_id,
        'fields': 'bdate,sex,interests,domain,city,country',
        'count': 1000
    }, VK_USER_TOKEN)
    count = 0
    for user in ria_female:
        try:
            User.create(nick=user.get('domain', user['id']),
                        birthdate=user.get('bdate'),
                        interests=user.get('interests', '').split(','),
                        source='vkontakte', sex=sex,
                        city=user.get('city', {}).get('title'),
                        country=user.get('country', {}).get('title'),
                        vk_id=user.get('id'))
        except:
            try:
                count += 1
                query = User.update(birthdate=user.get('bdate'),
                                    interests=user.get('interests', '').split(','),
                                    source='vkontakte', sex=sex,
                                    city=user.get('city', {}).get('title'),
                                    country=user.get('country', {}).get('title'),
                                    vk_id=user.get('id')).where(User.nick == user.get('domain', user['id']))
                query.execute()
                print(count)
            except Exception as exc:
                print(exc)
                continue


def create_messages(ids, filename):
    c = vk_api.get_users_messages(ids, VK_USER_TOKEN)

    with open('create_messages.json', 'w', encoding='utf8') as f:
        json.dump(c, f)

    with open(filename, 'w', encoding='utf8') as f:
        for i in c:
            author_id = User.get(User.vk_id == i['id'])
            if isinstance(i['messages'], dict):
                for b in i['messages']['items']:
                    try:
                        Message.create(link=vk_link_pattern.format(user_id=i['id'], message_id=b['id']),
                                       message=' '.join(b['text'].split('\n')),
                                       author=author_id,
                                       date=date.fromtimestamp(b['date']))
                        f.write(' '.join(b['text'].split('\n')) + '\n')

                    except Exception as exc:
                        print(exc)
                        continue


# create_ria_users('male')
# needed_male = []
# males = User.select().where(
#     (User.sex == 'male'))
# for user in males:
#     if len(user.messages) != 0:
#         continue
#     needed_male.append(user.vk_id)

needed_female = []
females = User.select().where(
    (User.sex == 'female'))
for user in females:
    if len(user.messages) != 0:
        continue
    needed_female.append(user.vk_id)
# print()
print(len(needed_female))
create_messages(needed_female, 'new_females_test.txt')
# write_messages(males, 'males.txt')
# write_messages(females, 'females.txt')
# ria_female = User.filter(User.sex == 'female')
#
# ids = [user.vk_id for user in ria_female]
# create_messages(ids, "test.txt")

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
