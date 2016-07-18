from flask_bcrypt import generate_password_hash
import datetime
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

    def following(self):
        """ The users that we are following."""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """get users following the current user"""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self

            )
        )

    @classmethod
    def create_User(cls, username, email, password, admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin)

        except peewee.IntegrityError:
            raise ValueError("User already exsits")


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


class Relationship(peewee.Model):
    from_user = peewee.ForeignKeyField(User, related_name='relationships')
    to_user = peewee.ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = (
            (['from_user', 'to_user'], True)

        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
