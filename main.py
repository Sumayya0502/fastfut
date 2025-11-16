import sqlite3


from aiogram import executor, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery

from bottons import *
from geopy.distance import distance
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage




storage = MemoryStorage()
apibot = '8447569725:AAGc3mgKprK4PFD0n0rZDbotKCcfVObsACE'
bot = Bot(apibot)
dp = Dispatcher(bot=bot,storage=storage)
admin = 7918430772




class UserRegisterState(StatesGroup):
    name_phone_address = State()
class OrderState(StatesGroup):
    order_something = State()
class Phone_address_state(StatesGroup):
    phone = State()
    address = State()




@dp.message_handler(commands='start')
async def start(message: Message):
    chatid = message.chat.id
    name = message.from_user.first_name
    database = sqlite3.connect('db.sqlite')
    cursor = database.cursor()
    cursor.execute("""SELECT name FROM products""")
    products = cursor.fetchall()
    cursor.execute("""SELECT chat_id FROM users WHERE chat_id = ?""", (chatid,))
    user = cursor.fetchone()
    if user:
        await bot.send_message(chatid, f'Xush kelibsiz {name}', reply_markup=products_menu_buttons(products))
    else:
        await bot.send_message(chatid,
                               f'Xush kelibsiz {name}. Ism telefon manzil kiriting vergul bilan: \n Ali, 998917871199, Bagdod shirinsuv')
        await UserRegisterState.name_phone_address.set()




@dp.message_handler(state=UserRegisterState.name_phone_address)
async def get_infouser(message: Message,state:FSMContext):
    chatid = message.chat.id
    text = message.text
    if  ',' in message.text:
        if len(text.split(',')) == 3:
            name, phone, address = text.split(',')
            database = sqlite3.connect('db.sqlite')
            cursor = database.cursor()

            cursor.execute("""SELECT chat_id FROM users WHERE chat_id = ?""", (chatid,))
            user = cursor.fetchone()
            if not user:
                await state.update_data(
                    {'ism': name,
                     'phone': phone,
                     'address': address}
                )
                cursor.execute("""INSERT INTO users(chat_id, name, phone, address)
                VALUES   (?,?,?,?)
                """, (chatid, name, phone, address))
                cursor.execute("""SELECT name FROM products""")
                products = cursor.fetchall()
                await bot.send_message(chatid, 'Royxatdan otdingiz', reply_markup=products_menu_buttons(products))
            else:
                cursor.execute("""SELECT name FROM products""")
                products = cursor.fetchall()
                await bot.send_message(chatid, 'Siz avval Royxatdan o\'tgansiz', reply_markup=products_menu_buttons(products))
            database.commit()
            database.close()
        await state.finish()


@dp.message_handler(text ="Asosiy menu")
async def mainmenu(message: Message):
    chatid = message.chat.id
    text = message.text.strip()
    await bot.send_message(chatid,"Asosiy menu",reply_markup=main_menu_button())


@dp.message_handler()
async def cart(message: Message,state:FSMContext):
    chatid = message.chat.id
    database = sqlite3.connect("db.sqlite")
    cursor = database.cursor()
    cursor.execute("SELECT product, price, count FROM cart WHERE chat_id = ?", (chatid,))
    products = cursor.fetchall()
    text = message.text
    chat_id = message.chat.id
    if text=="🛒 Savatcha":
        text = f"Mahsulotlar ro'yhati:\n\n"
        total = 0
        for name, price, count in products:
            text += f"{name}: {price}  x {int(count)} = {price * int(count)}\n"
            total += int(price) * int(count)
        text += f"Umumiy narx: {total}"
        data = await state.get_data()
        text += f"\n\nIsm: {data.get('ism', '')}\nTelefon: {data.get('phone', '')}\nManzil: {data.get('address', '')}"
        await bot.send_message(chatid, text=text, reply_markup=order_botton())
    elif text=="Orqaga":
        cursor.execute("""SELECT name FROM products""")
        products = cursor.fetchall()
        await bot.send_message(chatid, "Asosiy menyuga qaytdingiz", reply_markup=products_menu_buttons(products))

    elif text=='🍔 Fastfood':
        await bot.send_message(chat_id, 'Fast food', reply_markup=fastfuts_menu_buttons())

    elif text=="🥤 Ichimliklar":
        await bot.send_message(chat_id, 'Ichimliklar', reply_markup=fastfuts_menu_buttons())

    elif text=="🍰 Shirinliklar":
        await bot.send_message(chat_id, 'Shirinliklar', reply_markup=fastfuts_menu_buttons())

    elif  '🏷' in message.text:
        database = sqlite3.connect('db.sqlite')
        cursor = database.cursor()
        name = message.text.replace('🏷 ', '')
        cursor.execute("""SELECT  name, price, id FROM products WHERE name = ?""", (name,))
        product = cursor.fetchone()
        rasm = open(f'{product[0]}.jpg', 'rb')
        text = f'Maxsulot: {product[0]}\nNarxi: {product[1]}'
        await bot.send_photo(chat_id=chat_id, photo=rasm, caption=text, reply_markup=add_to_cart_button(product_id=product[2]))


    elif "Buyurtmani bekor qilish" in message.text:
        database = sqlite3.connect('db.sqlite')
        cursor = database.cursor()
        cursor.execute("DELETE FROM cart WHERE chat_id = ? AND complete = False ", (chatid,))
        database.commit()
        database.close()
        await bot.send_message(chatid,text = "Buyurtmangiz bekor qilindi")
    elif "Buyurtma berish" in message.text:
        cursor.execute("""SELECT * FROM cart WHERE chat_id = ? AND complete = False""",(chatid,))
        products = cursor.fetchall()
        await state.update_data({'products':products})
        await bot.send_message(chatid,  text="Buyurtmangiz qabul qilinishi uchun raqam jo'nating",reply_markup=phone_button())
        await Phone_address_state.phone.set()

    else:
        await bot.send_message(chatid,text = "Iltimos, tugmalardan birini bosing yoki /start tugmasi bilan qayta boshlang!")




@dp.callback_query_handler(lambda call:"add_cart" in call.data )
async def order(callback:CallbackQuery,state:FSMContext):
    _, name, product_id = callback.data.split('_')
    chatid = callback.message.chat.id
    database = sqlite3.connect('db.sqlite')
    cursor = database.cursor()
    cursor.execute('''SELECT name, price FROM products WHERE id = ?''', (product_id,))
    product = cursor.fetchone()

    cursor.execute("SELECT product, price, count FROM cart WHERE chat_id = ? AND complete = ?", (chatid, 0))
    karzinka = cursor.fetchone()

    if not karzinka:
        cursor.execute("INSERT INTO cart(chat_id, product, price,  count, complete) VALUES (?,?,?,?, ?)",
                           (chatid, product[0], product[1], 1, False))
    else:
        count = karzinka[2]
        cursor.execute("UPDATE cart SET count = ?  WHERE chat_id = ? AND complete = ?", (count + 1, chatid, False))
    database.commit()
    database.close()
    await bot.send_message(chatid, text="Buyurtmangiz saqlandi")


itc_lat = 40.460496
itc_lon = 71.212102


@dp.message_handler(content_types='contact', state=Phone_address_state.phone)
@dp.message_handler(state=Phone_address_state.phone)
async def getcontact(message: Message,state:FSMContext):
    chatid = message.chat.id
    if message.contact:
        telefon = message.contact.phone_number
        name = message.contact.first_name
        await bot.send_contact(admin,
                               phone_number=telefon, first_name=name)
        await state.update_data()
    elif message.text.isdigit():
        await state.update_data()
    await bot.send_message(chatid, text="lokatsiya jo'nating", reply_markup=lokatsiya_botton())
    await Phone_address_state.address.set()



@dp.message_handler(content_types='location', state=Phone_address_state.address)
async def getlocation(message: Message,state:FSMContext):
    chatid = message.chat.id
    latitude = message.location.latitude
    longitude = message.location.longitude
    masofa = distance(
        (itc_lat, itc_lon), (latitude, longitude)
    ).km
    masofa = round(masofa, 3)

    data=await state.get_data()
    await bot.send_message(chat_id=chatid, text=f'Siz turgan joydan oquv markazgacha {masofa} km')
    await bot.send_location(chatid, latitude=itc_lat, longitude=itc_lon)
    await bot.send_location(admin,latitude=itc_lat, longitude=itc_lon)
    await state.finish()




executor.start_polling(dp, skip_updates=True)