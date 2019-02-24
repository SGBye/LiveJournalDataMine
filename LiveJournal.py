import re
from datetime import datetime
import json

import networkx as nx
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import os

from bs4 import BeautifulSoup
from iso3166 import countries

from settings import *

import matplotlib.pyplot as plt


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

    @staticmethod
    def clean_tags(raw_html):
        """clean messages from html tags and quotes"""

        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        quotes = re.compile('&quot;')
        change_quoes = re.sub(quotes, '"', cleantext)
        return change_quoes

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
                if len(line) > 2:
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
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.ConnectionError
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
            for tag in soup.find_all('content', type='html'):
                if len(self.messages) < SENTENCES_TO_SHOW:
                    self.messages.append(self.clean_tags(tag.text))

    @classmethod
    def object(cls, nick):
        """simple fabric for objects"""
        return cls(nick)



if __name__ == "__main__":

    user = 'babs71'

    babs71 = LiveJournal.object(user)

    result = {fr: [] for fr in babs71.friends}
    print(result)
    count = 0
    length = len(babs71.friends)
    for i in babs71.friends:
        count += 1
        print(f'***User number {count} out of {length}, processing {i}...')
        try:
            temp_object = LiveJournal.object(i)
        except FileNotFoundError:
            print("File not found")
            continue
        for friend in temp_object.friends:
            if friend in babs71.friends:
                result[i].append(friend)

    with open('fof_babs71.json', 'w') as f:
        json.dump(result, f)
    print(result)

