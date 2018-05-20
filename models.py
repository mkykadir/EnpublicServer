from neomodel import StructuredNode, StructuredRel, StringProperty, FloatProperty, RelationshipTo, Relationship, \
    IntegerProperty


class Walk(StructuredRel):
    distance = FloatProperty(default=4)


class FrTo(StructuredRel):
    distance = FloatProperty(default=0)


class Vehicle(StructuredNode):
    code = StringProperty(required=True, unique_index=True)
    color = StringProperty(default="000000")
    description = StringProperty()

    to = RelationshipTo('Station', 'TO', model=FrTo)


class Station(StructuredNode):
    short = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    latitude = FloatProperty(required=True)
    longitude = FloatProperty(required=True)
    directed = IntegerProperty(default=0)
    nearby = IntegerProperty(default=0)
    searched = IntegerProperty(default=0)
    visited = IntegerProperty(default=0)

    fr = RelationshipTo('Vehicle', 'FR', model=FrTo)
    walk = Relationship('Station', 'WALK', model=Walk)


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
