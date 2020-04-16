import datetime

from models import Message, User

messages = Message.select()
# from_russia = []
# not_from_russia = []
from_big = []
not_from_big = []
#
# for message in messages:
#     if message.author.country is not None:
#         if message.author.country == 'Russian Federation':
#             from_russia.append(message)
#         else:
#             not_from_russia.append(message)
#

from users import LiveJournalUser
for message in messages:
    if message.author.city is not None:
        if 'petersburg' in message.author.city.lower() or message.author.city.lower() in ['москва', 'moscow', 'saint petersburg', 'spb']:
            from_big.append(message)
        else:
            not_from_big.append(message)
print(len(from_big))
print(len(not_from_big))
#
with open('from_big_10000.txt', 'w', encoding='utf8') as f:
    for message in from_big[:10000]:
        f.write(message.message + '\n')

with open('not_from_big_10000.txt', 'w', encoding='utf8') as f:
    for message in not_from_big[:10000]:
        f.write(message.message + '\n')


# babs = User.get(nick='babs71')
# for index, friend in enumerate(babs.friends[:10]):
#     count = 1
#     current_user = User.get(nick=friend)
#     for new_person in current_user.friends:
#         if not friend.startswith('_'):
#             print(f"Processing {count} of {index} out of {len(current_user.friends)}...")
#             user = LiveJournalUser(new_person)
#             user.fill_the_data()
#             count += 1


# with open('from_big.txt', 'r', encoding='utf8') as f:
#     a = f.read().split('\n')
#
# print(len(a))