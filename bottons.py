from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(text='🍔 Fastfood'),
        KeyboardButton(text='🥤 Ichimliklar'),
        KeyboardButton(text='🍰 Shirinliklar'),
    )
    markup.add(KeyboardButton(text='🛒 Savatcha'),
               KeyboardButton(text="Orqaga"))
    return markup


def products_menu_buttons(products):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='Asosiy menu'),
               KeyboardButton(text="🛒 Savatcha"),
               KeyboardButton(text="Orqaga"))
    for name in products:
        markup.add(KeyboardButton(text=f'🏷 {name[0]}'))
    return markup


def fastfuts_menu_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(text="🏷 burger"),
        KeyboardButton(text="🏷 lavash"),
        KeyboardButton(text="Orqaga"))
    return markup


def add_to_cart_button(product_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="Savatchaga qo'shish", callback_data=f"add_cart_{product_id}"))
    return markup

def order_botton():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(text = "Buyurtma berish"),
        KeyboardButton(text="Buyurtmani bekor qilish")
    )
    return markup

def phone_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(text='Raqam jonatish', request_contact=True))
    return markup

def lokatsiya_botton():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(        KeyboardButton(text='Lokatsiya jonatish', request_location=True))
    return markup