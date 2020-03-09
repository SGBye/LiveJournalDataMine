import logging
import re
import string
import time

import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import os

from bs4 import BeautifulSoup
from iso3166 import countries
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from peewee import IntegrityError

from settings import *
from models import User, Message, pg_db

log = logging.getLogger(__name__)


class LiveJournal:
    """
    describes the fields and functions for gathering the data from LiveJournal depending on nickname
    """

    def __init__(self, nick):
        self.nick = nick
        self.name = None
        self.friends = []  # done
        self.friend_of = []  # done
        self.conn_reads = []  # done
        self.conn_in = []  # done
        self.birthdate = None  # done
        self.city = None  # done
        self.country = None  # done
        self.schools = []  # done
        self.interests = []  # done
        self.about = None  # done
        self.messages = []
        self.title = None
        self.subtitle = None
        self.picture = None
        # add other features here

        self.process_personal_info()
        self.process_connections()
        self.process_messages()

    def __str__(self):
        return f'Ник: {self.nick}, имя: {self.name}, дата рождения: {self.birthdate}'

    def __repr__(self):
        return f'Ник: {self.nick}, имя: {self.name}, дата рождения: {self.birthdate}'

    @property
    def year_of_birth(self):
        return self.birthdate.split('-')[0] if self.birthdate else None

    @staticmethod
    def clean_tags(raw_html):
        """
        clean messages from html tags and quotes
        """

        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        quotes = re.compile('&quot;')
        change_quoes = re.sub(quotes, '"', cleantext)
        to_delete = re.compile("&\w+;")
        cleantext = re.sub(to_delete, '', change_quoes)
        return cleantext

    def _gather_personal_info(self):
        """
        first download the personal data from the internet.
        May be slower, but for now more polite.
        """

        filename = os.path.join('cache', f'{self.nick}', f'{self.nick}_profile.xml')
        data = requests.get(f'https://{self.nick}.livejournal.com/data/foaf',
                            params={'email': 'ctac1995@gmail.com'})

        # create folder to cache and write data
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_profile.xml'), 'w',
                  encoding='utf-8') as f:
            f.write(data.text)
        return data.text

    def process_personal_info(self):
        """
        process the xml downloaded from the internet or from local cache
        """

        try:
            tree = ET.parse(os.path.join('cache', f'{self.nick}', f'{self.nick}_profile.xml'))
        except FileNotFoundError:
            # retries logic
            for attempt in range(MAX_RETRIES):
                try:
                    tree = ET.ElementTree(ET.fromstring(self._gather_personal_info()))
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
                else:
                    break
            # if we failed all attempts, just forget about this guy
            else:
                return
        except ET.ParseError:
            log.debug('This user has either been deleted or never created: %s', self.nick)
            return

        root = tree.getroot()[0]

        for i in root:
            # get all the possible data from source
            if 'name' in i.tag:
                self.name = i.text
            elif 'journaltitle' in i.tag:
                self.title = i.text
            elif 'img' in i.tag:
                for key in i.attrib:
                    if 'resource' in key:
                        self.picture = i.attrib[key]
            elif 'journalsubtitle' in i.tag:
                self.subtitle = i.text
            elif 'dateOfBirth' in i.tag:
                self.birthdate = i.text
            elif 'city' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        self.city = unquote(i.attrib[key])
            elif 'country' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        try:
                            self.country = countries.get(i.attrib[key]).name
                        except KeyError:
                            self.country = i.attrib[key]
            elif 'school' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        self.schools.append(i.attrib[key])
            elif 'interest' in i.tag:
                for key in i.attrib:
                    if 'title' in key:
                        self.interests.append(i.attrib[key])
            elif 'bio' in i.tag:
                self.about = self.clean_tags(i.text)

    def _gather_connections(self):
        """
        first download the profile-connunities connections data from the internet.
        May be slower, but for now more polite.
        """
        data = requests.get(f'https://www.livejournal.com/misc/fdata.bml?conn=1&user={self.nick}',
                            params={'email': 'ctac1995@gmail.com'})
        with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_connections.txt'), 'w', encoding='utf-8') as f:
            f.write(data.text)
        return data.text

    def process_connections(self):
        """
        process the html downloaded from the internet or from local cache
        """

        try:  # if it's not the first call to user's data, we should use cache
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_connections.txt'),
                      encoding='utf-8') as f:
                data = f.readlines()
        except FileNotFoundError:
            # retries logic
            for attempt in range(MAX_RETRIES):
                try:
                    data = self._gather_connections()
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
                else:
                    break
            # failing all attempts makes us forget the guy
            else:
                return

        for line in data:
            if len(line) > 2:  # it's in the following format "C< username"
                if not line.startswith('#'):
                    if line.startswith('P>'):
                        self.friends.append(line.split()[1])
                    elif line.startswith("P<"):
                        self.friend_of.append(line.split()[1])
                    elif line.startswith("C>"):
                        self.conn_reads.append(line.split()[1])
                    else:
                        self.conn_in.append(line.split()[1])

    def _gather_messages(self):
        """
        first download the messages data from the internet.
        May be slower, but for now more polite.
        """
        data = requests.get(f'https://{self.nick}.livejournal.com/data/atom',
                            params={'email': 'ctac1995@gmail.com'})
        with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_messages.html'), 'w', encoding='utf-8') as f:
            f.write(data.text)
        return data.text

    def process_messages(self):
        """
        process the html downloaded from the internet or from local cache
        """

        try:
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_messages.html'), encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            # retries logic
            for attempt in range(MAX_RETRIES):
                try:
                    html = self._gather_messages()
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
                else:
                    break
            # failing all attempts makes us forget the guy
            else:
                return

        soup = BeautifulSoup(html, 'html.parser')
        try:
            a_user = User.create(**self.__dict__)
        except IntegrityError:
            print("exists")
            pg_db.rollback()
            return
        for tag in soup.find_all('entry'):
            if len(self.messages) < SENTENCES_TO_SHOW:
                message = ''
                if tag.content:
                    message = self.clean_tags(tag.content.text)
                elif tag.summary:
                    message = self.clean_tags(tag.summary.text)
                Message.create(message=message, author=a_user,
                               link=tag.link['href'],
                               date=tag.published.text.split('T')[0])


class LiveJournalMessage:

    def __init__(self, author, message, link, date):
        self.author = author
        self.message = message
        self.link = link
        self.date = date

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.author}: {self.message[:50]}..."

    @property
    def symbols_count(self):
        return len(self.message)

    @staticmethod
    def tokenize_words(message):
        return [i for i in word_tokenize(message) if i not in string.punctuation]

    @property
    def words_count(self):
        return len(self.message.tokenize_words())

    @property
    def sentences_count(self):
        return len(sent_tokenize(self.message, 'russian'))

    @property
    def comas(self):
        return self.message.count(",")

    @property
    def tires(self):
        return self.message.count("-") + self.message.count("—")

    @property
    def first_sentence(self):
        return sent_tokenize(self.message, 'russian')[0]

    @property
    def last_sentence(self):
        return sent_tokenize(self.message, 'russian')[-1]


if __name__ == "__main__":
    needed_users = ['babs71', 'seminarist', 'nomen-nescio']
    objects = []
    count = 1
    babs = LiveJournal('babs71')
    for friend in babs.friends:
        if not friend.startswith('_'):
            print(f"Processing {count} out of {len(babs.friends)}...")
            LiveJournal(friend)
            count+=1

