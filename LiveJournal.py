import re
import string

import nltk as nltk
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import os

from bs4 import BeautifulSoup
from iso3166 import countries
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


from settings import *



class LiveJournal:
    """descirbes the fields and functions for gathering the data from LiveJournal depending on nickname"""

    def __init__(self, nick):
        self.nick = nick
        self.name = None
        self.friends = []  # done
        self.frind_of = []  # done
        self.comm_reads = []  # done
        self.comm_in = []  # done
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

        self.get_personal_info()
        self.get_connections()
        self.get_messages()

    def __str__(self):
        return f'Ник: {self.nick}, имя: {self.name}, дата рождения: {self.birthdate}'

    def __repr__(self):
        return f'Ник: {self.nick}, имя: {self.name}, дата рождения: {self.birthdate}'

    @property
    def year_of_birth(self):
        return self.birthdate.split('-')[0] if self.birthdate else None

    @staticmethod
    def clean_tags(raw_html):
        """clean messages from html tags and quotes"""

        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        quotes = re.compile('&quot;')
        change_quoes = re.sub(quotes, '"', cleantext)
        to_delete = re.compile("&\w+;")
        cleantext = re.sub(to_delete, '', change_quoes)
        return cleantext

    def _gather_personal_info(self):
        """first download the personal data from the internet.
               May be slower, but for now more polite."""

        filename = os.path.join('cache', f'{self.nick}', f'{self.nick}_profile.xml')
        try:
            data = requests.get(f'https://{self.nick}.livejournal.com/data/foaf',
                                params={'email': 'ctac1995@gmail.com'})
        except requests.exceptions.RequestException:
            raise requests.exceptions.ConnectionError
        else:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_profile.xml'), 'w',
                      encoding='utf-8') as f:
                f.write(data.text)


    def get_personal_info(self):
        """process the xml downloaded from the internet or from local cache"""

        try:
            tree = ET.parse(os.path.join('cache', f'{self.nick}', f'{self.nick}_profile.xml'))
        except FileNotFoundError:
            try:
                self._gather_personal_info()
            except requests.exceptions.ConnectionError:
                return
            else:
                self.get_personal_info()
        except ET.ParseError:
            print('This user has either been deleted or never created.')
        else:
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
        """first download the profile-communities connections data from the internet.
        May be slower, but for now more polite."""

        try:
            data = requests.get(f'https://www.livejournal.com/misc/fdata.bml?comm=1&user={self.nick}',
                                params={'email': 'ctac1995@gmail.com'})
        except requests.exceptions.RequestException:
            print(os.path.join('cache', f'{self.nick}', f'{self.nick}_connections.txt'))
            raise requests.exceptions.ConnectionError
        else:
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_connections.txt'),
                      'w', encoding='utf-8') as f:
                f.write(data.text)

    def get_connections(self):
        """process the html downloaded from the internet or from local cache"""

        try:  # if it's not the first call to user's data, we should use cache
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_connections.txt'),
                      encoding='utf-8') as f:
                data = f.readlines()
        except FileNotFoundError:
            try:
                self._gather_connections()
            except requests.exceptions.ConnectionError:
                return
            else:
                self.get_connections()
        else:
            for line in data:
                if len(line) > 2:  #  it's in the following format "C< username"
                    if not line.startswith('#'):
                        if line.startswith('P>'):
                            self.friends.append(line.split()[1])
                        elif line.startswith("P<"):
                            self.frind_of.append(line.split()[1])
                        elif line.startswith("C>"):
                            self.comm_reads.append(line.split()[1])
                        else:
                            self.comm_in.append(line.split()[1])

    def _gather_messages(self):
        """first download the messages data from the internet.
        May be slower, but for now more polite."""

        try:
            data = requests.get(f'https://{self.nick}.livejournal.com/data/atom',
                                params={'email': 'ctac1995@gmail.com'})
        except requests.exceptions.RequestException:
            raise requests.exceptions.ConnectionError
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_messages.html'), 'w', encoding='utf-8') as f:
                    f.write(data.text)

    def get_messages(self):
        """process the html downloaded from the internet or from local cache"""

        try:
            with open(os.path.join('cache', f'{self.nick}', f'{self.nick}_messages.html'), encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            try:
                self._gather_messages()
            except requests.exceptions.ConnectionError:
                return
            else:
                self.get_messages()
        else:
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup.find_all('entry'):
                if len(self.messages) < SENTENCES_TO_SHOW:
                    message = ''
                    if tag.content:
                        message = self.clean_tags(tag.content.text)
                    elif tag.summary:
                        message = self.clean_tags(tag.summary.text)

                    self.messages.append(LiveJournalMessage(message=message, author=self.nick,
                                                            link=tag.link['href'], date=tag.published.text.split('T')[0]))

    @classmethod
    def object(cls, nick):
        """simple fabric for objects"""
        return cls(nick)


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
    count = 0
    babs = LiveJournal.object('babs71')

    for friend in babs.friends:
        count += 1
        print(f"{count}... {friend} appending. Continuing...")
        if friend.startswith("_"):
            print(f"*******Skipped {friend}. Continuing")
            continue
        objects.append(LiveJournal.object(friend))
    print(len(objects))

