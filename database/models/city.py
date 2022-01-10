from mongoengine.fields import Document,DictField,StringField

class City(Document):
    name = DictField()
    url = StringField()