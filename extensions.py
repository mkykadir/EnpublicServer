import os
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore, UserMixin, RoleMixin
from neomodel import config, db

config.DATABASE_URL = os.environ['ENPUBLIC_DB_URL']

user_db = MongoEngine()
neo_db = db


class Stats(user_db.EmbeddedDocument):
    searched = user_db.IntField(default=0)
    directed = user_db.IntField(default=0)
    vehicles = user_db.IntField(default=0)
    walked = user_db.IntField(default=0)
    vehicled = user_db.IntField(default=0)


class Achievement(user_db.Document):
    name = user_db.StringField(unique=True, required=True, max_length=100)
    description = user_db.StringField(required=True, max_length=150)
    required = user_db.IntField(required=True)
    stats_id = user_db.StringField(required=True)


class Role(user_db.Document, RoleMixin):
    name = user_db.StringField(max_length=80, unique=True)
    description = user_db.StringField(max_length=255)


class User(user_db.Document, UserMixin):
    email = user_db.StringField(max_length=255, unique=True)
    password = user_db.StringField(max_length=255)
    full_name = user_db.StringField(max_length=255)
    active = user_db.BooleanField(default=True)
    roles = user_db.ListField(user_db.ReferenceField(Role), default=[])
    achieved = user_db.ListField(user_db.ReferenceField(Achievement), default=[])
    stats = user_db.EmbeddedDocumentField(Stats, default=Stats())

    def has_role(self, role):
        for m_role in self.roles:
            if m_role.name == role:
                return True

        return False


user_datastore = MongoEngineUserDatastore(user_db, User, Role)

security = Security()
