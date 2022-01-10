from mongoengine.fields import Document,DictField,StringField

class State(Document):
    name = DictField()
    url = StringField()