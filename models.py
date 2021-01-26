import datetime
from peewee import *

db = SqliteDatabase('KFC_orm.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = IntegerField(primary_key=True, null=False)
    name = TextField()
    username = TextField()


class Category(BaseModel):
    id = IntegerField(primary_key=True)
    name = TextField()


class Product(BaseModel):
    id = IntegerField(primary_key=True)
    name = TextField()
    category = ForeignKeyField(Category, backref='products')
    price = DecimalField(max_digits=4, decimal_places=2)


class ProductPhoto(BaseModel):
    id = ForeignKeyField(Product)
    url = TextField()


class Cart(BaseModel):
    owner_id = ForeignKeyField(User, backref='cart')
    product_id = ForeignKeyField(Product)
    amount = IntegerField(default=0)


db.create_tables([User, Category, Product, Cart, ProductPhoto])
