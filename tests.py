from telegram.ext import Updater
from peewee import SqliteDatabase
from models import db, User, Cart
import unittest
from unittest.mock import Mock
from main import Store


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db.transaction() as txn:
            test_func(*args, **kwargs)
            txn.rollback()
    return wrapper


class FromUser:
    def __init__(self):
        self.id = 123
        self.first_name = 'ivan'
        self.username = 'IvanTester'


class Message:
    def __init__(self, from_user):
        self.from_user = from_user

    def reply_text(self, *args, **kwargs):
        return Mock()


class Update:
    def __init__(self, message):
        self.message = message


# Класс update для работы бота
update = Update(message=Message(FromUser()))
context = {}


class TestBot(unittest.TestCase):

    @isolate_db
    def test_new_user(self):

        global update

        # Проверяем, есть ли пользователь в базе.
        user_before = bool(User.get(User.id == update.message.from_user.id))
        try:
            user_before = bool(User.get(User.id == update.message.from_user.id))
        except IndexError as exc:
            user_before = False

        # Создаем нового пользователя, если его нет
        Store().start(update, context)

        # Проверяем еще раз
        try:
            user_after = User.get(User.id == update.message.from_user.id)
        except IndexError as exc:
            user_after = False
        # Если пользователя нет в БД, то он должен быть успешно добавлен
        self.assertEqual(not user_before, bool(user_after), msg='Пользователь не создан')
        self.assertEqual(user_after.name, update.message.from_user.first_name, msg='Имя нового пользователя не корректно')


    @isolate_db
    def test_add_to_cart(self):
        # Создаем нулевое кол-во продуктов в корзине для пользователя.
        # Создание происходит при просмотре инфо продукта
        product_in_cart, created = Cart.get_or_create(owner_id=update.message.from_user.id, product_id=1)
        self.assertTrue(created, 'Продукт не создан в корзине')

        # тестовый объект магазина
        store = Store()
        store.user = update.message.from_user
        store.current_product = Mock()
        store.current_product.id = 1

        update.callback_query = Mock()

        product_to_add = 5
        for count in range(1, product_to_add+1):
            store.cart_put_one(update, context)
            product_in_cart.amount += 1
            product_in_cart.save()

        # Проверка кол-ва после добавления
        product_in_cart = Cart.get(owner_id=update.message.from_user.id, product_id=1)
        self.assertEqual(product_to_add, product_in_cart.amount, 'Неверно работает добавление продукта')


    @isolate_db
    def test_clear_cart(self):
        # тестовый объект магазина
        store = Store()
        store.user = update.message.from_user
        store.current_product = Mock()
        store.current_product.id = 1

        expected_products = [(1, 3), (2, 2), (3, 1)]

        # Наполняем корзину
        for product_id, product_count in expected_products:
            Cart.create(owner_id=store.user.id, product_id=product_id, amount=product_count)

        # Проверяем корректность наполнения
        cart_content = Cart.select().where(Cart.owner_id == store.user.id)
        for expected, in_cart in zip(expected_products, cart_content):
            self.assertEqual(expected, (in_cart.product_id.id, in_cart.amount), 'Что-то не так при пополнении корзины')

        store.cart_remove_all(update, context)

        # проверяем, что корзина очищена
        cart_after_cleaning = Cart.select().where(Cart.owner_id == store.user.id)
        for record in cart_after_cleaning:
            self.assertEqual(record.amount, 0, 'Продукт не удален из корзины')


if __name__ == '__main__':
    unittest.main()
