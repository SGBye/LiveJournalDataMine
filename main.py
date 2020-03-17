import datetime

from models import Message, User

# messages = Message.select()
# # authors = User.select().where(User.birthdate.is_null(False))
# authors = User.select()
# below_thirty = []
# above_thirty = []
#
# for message in messages:
#     birth_date = message.author.birthdate
#     bd_split = birth_date.split('-') if birth_date is not None else None
#     if birth_date and len(bd_split) > 2:
#         year = int(bd_split[0])
#         if 2019 - year > 30:
#             above_thirty.append(message)
#         else:
#             below_thirty.append(message)
from users import LiveJournalUser

babs = LiveJournalUser('sgbye')
babs.fill_the_data()

# for index, friend in enumerate(babs.friends[:10]):
#     count = 1
#     current_user = User.get(nick=friend)
#     for new_person in current_user.friends:
#         if not friend.startswith('_'):
#             print(f"Processing {count} of {index} out of {len(current_user.friends)}...")
#             LiveJournal(new_person)
#             count += 1


