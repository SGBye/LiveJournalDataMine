import os

SENTENCES_TO_SHOW = 5
MAX_RETRIES = 5
VK_TOKEN = os.environ.get('VK_TOKEN')
VK_NEEDED_PROFILE_FIELDS = ("about", "activities", "bdate", "city", "country", "education",
                            "id", "first_name", "last_name", "interests")
