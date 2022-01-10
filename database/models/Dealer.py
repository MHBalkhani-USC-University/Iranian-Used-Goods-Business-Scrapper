from mongoengine.fields import Document,DictField,StringField

class Dealer(Document):
    name = DictField()
    phone = StringField()