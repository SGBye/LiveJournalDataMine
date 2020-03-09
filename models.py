import peewee
from playhouse.postgres_ext import ArrayField

pg_db = peewee.PostgresqlDatabase('diplom_data', user='test_stas', password='12345',
                                  host='0.0.0.0', port=5432)


class User(peewee.Model):
    nick = peewee.TextField(unique=True)
    name = peewee.TextField(null=True)
    friends = ArrayField(peewee.TextField, null=True)
    friend_of = ArrayField(peewee.TextField, null=True)
    conn_reads = ArrayField(peewee.TextField, null=True)
    conn_in = ArrayField(peewee.TextField, null=True)
    birthdate = peewee.TextField(null=True)
    city = peewee.TextField(null=True)
    country = peewee.TextField(null=True)
    schools = ArrayField(peewee.TextField, null=True)
    interests = ArrayField(peewee.TextField, null=True)
    about = peewee.TextField(null=True)
    title = peewee.TextField(null=True)
    subtitle = peewee.TextField(null=True)
    picture = peewee.TextField(null=True)

    class Meta:
        database = pg_db


class Message(peewee.Model):
    author = peewee.ForeignKeyField(User, backref='messages')
    message = peewee.TextField()
    link = peewee.TextField()
    date = peewee.TextField()

    class Meta:
        database = pg_db

    @property
    def symbols_count(self):
        return len(self.message)

    # @staticmethod
    # def tokenize_words(message):
    #     return [i for i in word_tokenize(message) if i not in string.punctuation]
    #
    # @property
    # def words_count(self):
    #     return len(self.message.tokenize_words())
    #
    # @property
    # def sentences_count(self):
    #     return len(sent_tokenize(self.message, 'russian'))
    #
    # @property
    # def comas(self):
    #     return self.message.count(",")
    #
    # @property
    # def tires(self):
    #     return self.message.count("-") + self.message.count("—")
    #
    # @property
    # def first_sentence(self):
    #     return sent_tokenize(self.message, 'russian')[0]
    #
    # @property
    # def last_sentence(self):
    #     return sent_tokenize(self.message, 'russian')[-1]


pg_db.create_tables([User, Message])
