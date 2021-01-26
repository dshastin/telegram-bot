from peewee import *

db = SqliteDatabase('people.db')


class Person(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db # This model uses the "people.db" database.

categories = [
    'Новинки',
    'Бургеры',
    'Баскеты',
    'Соусы',
    'Холодные напитки',
    'Кофе и чай'
]

