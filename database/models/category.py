from mongoengine.fields import EmbeddedDocument,StringField

class Category(EmbeddedDocument):
    name = StringField()
    url = StringField()