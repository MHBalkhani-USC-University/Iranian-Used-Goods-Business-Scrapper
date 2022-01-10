from mongoengine.fields import Document,DictField,StringField,ListField,ReferenceField
from .city import City
from .state import State

class Ad(Document):
    name = DictField()
    city = ReferenceField(City)
