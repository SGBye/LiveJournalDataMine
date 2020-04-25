import datetime
import os

from models import Message, User

# users = User.select().where(User.source != 'vkontakte')
messages = Message.select()
# from_russia = []
# not_from_russia = []
from_big = []
not_from_big = []
# print(len(users))
# for message in messages:
#     if message.author.country is not None:
#         if message.author.country == 'Russian Federation':
#             from_russia.append(message)
#         else:
#             not_from_russia.append(message)
#
# print(len(messages))
from users import LiveJournalUser
for message in messages:
    if message.author.city is not None:
        if 'petersburg' in message.author.city.lower() or message.author.city.lower() in ['москва', 'moscow', 'saint petersburg', 'spb']:
            from_big.append(message)
        else:
            not_from_big.append(message)
print(len(from_big))
print(len(not_from_big))
# #
# with open('from_big_10000.txt', 'w', encoding='utf8') as f:
#     for message in from_big[:10000]:
#         f.write(message.message + '\n')
#
# with open('not_from_big_10000.txt', 'w', encoding='utf8') as f:
#     for message in not_from_big[:10000]:
#         f.write(message.message + '\n')


# babs = User.get(nick='smitrich')
# print(babs.friends)
#
# for index, friend in enumerate(babs.friends[10:20]):
#     count = 1
#     try:
#         a = User.get(nick=friend)
#     except:
#         a = LiveJournalUser(nick=friend)
#         a.fill_the_data()
#
#     for new_person in a.friends:
#         if not new_person.startswith('_'):
#             print(f"Processing {count} of {index} out of {len(a.friends)}...")
#             try:
#                 user = User.get(nick=new_person)
#             except:
#                 user = LiveJournalUser(new_person)
#                 user.fill_the_data()
#             count += 1
#     count = 1
# sgbye = LiveJournalUser('sgbye')
# sgbye.fill_the_data()

# with open('from_big.txt', 'r', encoding='utf8') as f:
#     a = f.read().split('\n')
#
# print(len(a))

# nicks = [name for name in os.listdir("./cache")]
#
# count = 1
# total = len(nicks)
# for nick in nicks:
#     print(f"Processing {count} of {total}...")
#     user = LiveJournalUser(nick=nick)
#     user.fill_the_data()
below_30 = []
above_30 = []
