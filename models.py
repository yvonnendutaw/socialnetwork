import datetime

from flask_bcrypt import generate_password_hash

from flask_login import UserMixin

import peewee
from sqlalchemy import ForeignKey

DATABASE = peewee.PostgresqlDatabase('network', user="postgres")


class User(UserMixin, peewee.Model):
    username = peewee.CharField(unique=True)
    email = peewee.CharField(unique=True)
    password = peewee.CharField(max_length=100)
    joined_at = peewee.DateTimeField(default=datetime.datetime.now)
    is_admin = peewee.BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)

        except peewee.IntegrityError:
            raise ValueError('User already exists')


class Post(peewee.Model):
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    user = peewee.ForeignKeyField(
        rel_model=User,
        related_name='posts'

    )
    content = peewee.TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)

class Student(UserMixin, peewee.Model):
    username = peewee.CharField(unique=True)
    email = peewee.CharField(unique=True)
    password = peewee.CharField(max_length=100)
    joined_at = peewee.DateTimeField(default=datetime.datetime.now)
    is_admin = peewee.BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Student], safe=True)
    DATABASE.close()
