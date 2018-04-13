import bcrypt
from neomodel import StructuredNode, StructuredRel, StringProperty, DateTimeProperty, IntegerProperty, RelationshipTo, \
    FloatProperty, Relationship


class Achievement(StructuredNode):
    key = StringProperty(unique_index=True, required=True)
    description = StringProperty(required=True)
    req_value = IntegerProperty(required=True)


class Achieved(StructuredRel):
    since = DateTimeProperty(default_now=True)


class User(StructuredNode):
    name = StringProperty(required=True)
    username = StringProperty(unique_index=True, required=True)
    email = StringProperty(required=True)
    salt = StringProperty(required=True)
    hash = StringProperty(required=True)
    created_date = DateTimeProperty(default_now=True)

    achievements = RelationshipTo('Achievement', 'ACHIEVED', model=Achieved)

    @staticmethod
    def get_salt_hash(password_text):
        salt_value = bcrypt.gensalt()
        hash_value = bcrypt.hashpw(str.encode(password_text), salt_value)
        return salt_value, hash_value

class Vehicle(StructuredRel):
    code = StringProperty(unique_index=True, required=True)
    color = StringProperty(default="000000")
    description = StringProperty()
    distance = FloatProperty(required=True, default=1.0)


class Station(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    latitude = FloatProperty(required=True)
    longitude = FloatProperty(required=True)
    nearby = IntegerProperty(default=0)
    searched = IntegerProperty(default=0)
    visited = IntegerProperty(default=0)

    connects = Relationship('Station', 'CONNECTS', model=Vehicle)

