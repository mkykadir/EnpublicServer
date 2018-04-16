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
        hash_value = bcrypt.hashpw(str.encode(password_text), str.encode(salt_value))
        return salt_value, hash_value

    @staticmethod
    def get_hash(salt_value, password_text):
        return bcrypt.hashpw(str.encode(password_text), str.encode(salt_value))


class Vehicle(StructuredRel):
    code = StringProperty(required=True)
    color = StringProperty(default="000000")
    description = StringProperty()
    distance = FloatProperty(default=1.0)

    @staticmethod
    def find_different_vehicles(relations):
        return_info = ''
        last_line = ''
        for relation in relations:
            current_line = relation.properties['code']
            if last_line != current_line:
                last_line = current_line + ' - '
                return_info += last_line

        if len(return_info) > 0:
            return return_info[0:len(return_info)-3]
        else:
            return ''


class Station(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    latitude = FloatProperty(required=True)
    longitude = FloatProperty(required=True)
    directed = IntegerProperty(required=True)
    nearby = IntegerProperty(default=0)
    searched = IntegerProperty(default=0)
    visited = IntegerProperty(default=0)

    connects = Relationship('Station', 'CONNECTS', model=Vehicle)

