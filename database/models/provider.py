from mongoengine.fields import Document,DictField,StringField

class Provider(Document):
    name = DictField()
    url = StringField()