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


class Activity:
    type = None
    start_time = None
    end_time = None
    locations = []

    def __init__(self, type, start_time, end_time):
        self.type = type
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def add_locations(activities, locations):
        result = activities

        for activity in result:
            start_time = activity.start_time
            end_time = activity.end_time

            for location in locations:
                if location.within_time(start_time, end_time):
                    activity.locations.append(location)

        return result

    @staticmethod
    def transitions_to_activity(transitions):
        result = []
        i = 0
        while i < len(transitions):
            starting = transitions[i]
            if starting.transition_type == 0:
                ending = transitions[i+1]
                if ending.transition_type == 1:
                    if starting.activity_type == ending.activity_type:
                        result.append(Activity(starting.activity_type, starting.timestamp, ending.timestamp))

            i = i+2

        return result

    @staticmethod
    def merge_nears(activities):
        result = activities

        i = 0
        while i < len(result):
            if i + 1 < len(result):
                current = result[i]
                next = result[i + 1]
                difference_in_time = next.start_time - current.end_time

                if 0 <= difference_in_time <= 120000:
                    current.end_time = next.end_time
                    del result[i+1]
                else:
                    i = i+1
            else:
                break

        return result


class Transition:
    activity_type = None
    transition_type = None
    timestamp = None

    def __init__(self, activity_type, transition_type, timestamp):
        self.activity_type = activity_type
        self.transition_type = transition_type
        self.timestamp = timestamp


class Location:
    latitude = None
    longitude = None
    timestamp = None
    speed = None
    accuracy = None

    def __init__(self, latitude, longitude, timestamp, speed, accuracy):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.speed = speed
        self.accuracy = accuracy

    def within_time(self, start_time, end_time):
        return end_time >= self.timestamp >= start_time
