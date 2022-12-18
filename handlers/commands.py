# Импорт классов и функций библиотеки aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup

# Импортируем текст кнопка
from keyboards import *
# Импортируем класс работы с базой данных
from lib.mdb import Mdb

# Импортируем классы для работы с состоянием
from states import Buy, Sell

import json
import requests
from datetime import datetime

# Импорт бибилиотеки для работы с базой данных mongodb
import pymongo

# Подключение к локальной базе данных mongodb
connect = pymongo.MongoClient(
    f'mongodb://localhost:27017/')

db = connect["database"]

# Коллекция данных с пользователями
db_users = db["users"]

# Коллекция данных дневников
db_diary = db["diary"]

# Коллекция данных портфелей пользователей
db_portfolio = db["portfolio"]

# Подключаем класс для работы с базой данных
mdb = Mdb(db_users, db_diary, db_portfolio)


def is_int_or_float(item:int) -> bool:
    """Функция для проверки передаваемого значения"""

    try:
        i = float(item)
    except:
        return False
    return True


def BTCUSDT_or_ETHUSDT(coin:str) -> bool:
    """Функция для проверки передаваемого значения"""
    if str(coin) == "BTCUSDT" or str(coin) == "ETHUSDT":
        try:
            coin = str(coin)
        except Exception as err:
            return False
    else:
        return False
    return True


async def cmd_start(message: types.Message):
    """ Название функции: Фнукция срабатывает при нажатии на /start"""

    # Формируем картинку
    image = types.InputFile('img/trade.jpg')

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(balance, portfolio)
    markup.add(diary, course)
    markup.add(setting)

    # ID пользователя телеграмм
    cid = message.chat.id

    # Получем текущую дату
    dt = datetime.now() 
    timestamp = datetime.timestamp(dt)
    
    # Делаем проверку на существование пользователя
    if not mdb.is_user(cid):
        # Пользователь не найден переходим к его регистрации в базе данных
        # Регестрируем пользователя в базе данных если его нет в базе
        new_user = dict(cid=cid, usdt=0, btc=0, eth=0, timestamp=timestamp)
        db_users.insert_one(new_user)

    # Отправляем сообщение пользователю
    await message.answer_photo(photo=image, caption="Привет! Это бот для криптовалютного инвестора. Пользуйся на здоровье :)", reply_markup=markup)


async def cmd_start_menu(message: types.Message):
    """Функция отдает главное меню"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(balance, portfolio)
    markup.add(diary, course)
    markup.add(setting)

    # Отправляем сообщение пользователю
    await message.answer(f"Привет! Это бот для криптовалютного инвестора. Пользуйся на здоровье :)", reply_markup=markup)


async def cmd_start_diary(message: types.Message):
    """Функция отдает Дневник"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(buy, sell)
    markup.add(menu, all_notes)
    markup.add(setting)

    # Отправляем сообщение пользователю
    await message.answer("Это ваш дневник. Добавте покупку или продажу", reply_markup=markup)


async def setting_user(message: types.Message):
    """Функция настроек пользователя"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(menu, reset)

    # Отправляем сообщение пользователю
    await message.answer(f"В этом разделе вы можете сбросить свой аккаунт.\n!!! Внимание все данные будут очищены", reply_markup=markup)


async def reset_user(message: types.Message):
    """Функция очистки аккаунта"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(balance, portfolio)
    markup.add(diary, course)
    markup.add(setting)

    # Получаем id пользователя
    cid = message.chat.id

    # Очищаем все записи
    db_diary.delete_many({"cid":cid})

    # Делаем обновление баланса пользователя в базе данных
    db_users.update_one({"cid" : cid},{"$set":{"usdt": 0, "btc": 0, "eth": 0}})

    # Отправляем сообщение пользователю
    await message.answer(f"Ваши данные успешно очищены", reply_markup=markup)

async def get_balance(message: types.Message):
    """Получаем баланс пользователя"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(balance, portfolio)
    markup.add(diary, course)
    markup.add(setting)

    # Получаем id пользователя
    cid = message.chat.id

    # Получаем данные пользователя из базы данных db_users по ID пользователя (cid)
    user = db_users.find_one({"cid":cid})

    # Записываем балансы пользовтаеля в переменную 
    balance_usdt = user["usdt"]
    balance_btc = user["btc"]
    balance_eth = user["eth"]

    # Среднее значение потраченных средств за покупку монет
    
    # Делаем условие и проверяем есть ли записи в дневнике и если нет то не делаем рассчет средней
    if not db_diary.find_one({"coin": "BTCUSDT", "side": "Покупка", "cid": cid}):
        average_value_btc = 0
    else:
        buy_btc_usdt = 0
        amount_btc = 0
        # Получем все записи покупок биткоина за доллары
        notes_buy_btc_usdt = db_diary.find({"coin": "BTCUSDT", "side": "Покупка", "cid": cid})
        for n in notes_buy_btc_usdt:
            # Делаем перебор по всем записям и складываем значения
            buy_btc_usdt = float(buy_btc_usdt) + float(n["amount_usdt"])
            amount_btc = float(amount_btc) + float(n["amount_coin"])

        # Средняя по формуле
        average_value_btc = float(buy_btc_usdt) / float(amount_btc)
        average_value_btc = "%.2f" % average_value_btc

    # Делаем условие и проверяем есть ли записи в дневнике и если нет то не делаем рассчет средней
    if not db_diary.find_one({"coin": "ETHUSDT", "side": "Покупка", "cid": cid}):
        average_value_eth = 0
    else:
        buy_eth_usdt = 0
        amount_eth = 0
        # Получем все записи покупок эфириума за доллары
        notes_buy_eth_usdt = db_diary.find({"coin": "ETHUSDT", "side": "Покупка", "cid": cid})
        for n in notes_buy_eth_usdt:
            # Делаем перебор по всем записям и складываем значения
            buy_eth_usdt = float(buy_eth_usdt) + float(n["amount_usdt"])
            amount_eth = float(amount_eth) + float(n["amount_coin"])

        # Средняя по формуле
        average_value_eth = float(buy_eth_usdt) / float(amount_eth)
        average_value_eth = "%.2f" % average_value_eth

    # Формируем ответ для пользователя
    txt_answer = f"Баланс USDT: {balance_usdt}" + f"\nБаланс BTC: {balance_btc}" + f"\nБаланс ETH: {balance_eth}" + f"\n\nСредняя цена BTC: {average_value_btc}\nСредняя цена ETH: {average_value_eth}"

    # Отправляем сообщение пользователю
    await message.answer(txt_answer, reply_markup=markup)


async def get_portfolio(message: types.Message):
    """Портфель пользователя"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(balance, portfolio)
    markup.add(diary, course)
    markup.add(setting)

    # Получаем список монет из базы данных
    coins = db_portfolio.find({})

    txt_coins = ""

    # Проходим циклом по каждой монете
    for coin in coins:
        # Отправляем сообщение пользователю по каждой монете отдельно
        txt_coins = txt_coins + f"Монета: {coin['coin']}\n"

    await message.answer(txt_coins, reply_markup=markup)


async def get_course(message: types.Message):
    """Получаем курс Монеты"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(balance, portfolio)
    markup.add(diary, course)
    markup.add(setting)

    # Получаем список монет из базы данных
    coins = db_portfolio.find({})

    # Определеяем переменную в которую будет записывать финальный текст для пользователя
    text_res = ""

    # Проходим циклом по каждой монете
    for coin in coins:

        # Формируем url запроса для получения данных по монете
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin['coin']}"
        res = requests.get(url)  
        res = res.json()
        
        # Формируем переменную в которую записываем стоимость монеты после ответа на запрос 
        price_coin = "%.2f" % float(res["price"])

        # Формируем запрос для получения процента отклонения цена за 24 часа
        url = f"https://api.binance.com/api/v1/ticker/24hr?symbol={coin['coin']}"
        res = requests.get(url)  
        res = res.json()

        percent_change = "%.2f" % float(res["priceChangePercent"])

        icon = "⬇️" if float(percent_change) < 0 else "⬆️"

        # Формируем финальный текст для пользвоателя
        text_res = text_res + f"\nМонета: {coin['coin']} \nЦена: {price_coin} USDT  \nИзменение 24H: {icon}  {percent_change} %\n" 

    # Отправляем сообщение пользователю
    await message.answer(text_res, reply_markup=markup)


async def get_all_diary(message: types.Message):
    """Получаем все записи"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(buy, sell)
    markup.add(menu, all_notes)

    # ID пользователя телеграмм
    cid = message.chat.id

    # Делаем запрос в базу данных для получения всех записей
    notes = db_diary.find({"cid": cid})

    # Определеяем переменную в которую будет записывать финальный текст для пользователя
    all_notes_text = ""

    # Проходим циклом по каждой записи
    for note in notes:

        # Формируем ответ для пользвоателя 
        timestamp = datetime.fromtimestamp(note['timestamp']).strftime("%d-%m-%y %H:%M") if note['timestamp'] else "Нет даты"
        all_notes_text = all_notes_text + "" + f"Дата: {timestamp} Тип: {note['side']}\nМонета: {note['coin']} Колличество монет: {note['amount_coin']}\nПо курсу: {note['price']}\n\n"

    # Создаем условие с проверкой. Если записей нет в базе данных то сообщаем об этом пользователю иначе выдаем список записей 
    if not all_notes_text:
        # Отправляем сообщение пользователю
        await message.answer("У Вас пока нет записей в дневнике", reply_markup=markup)
    else:
        # Отправляем сообщение пользователю
        await message.answer(all_notes_text, reply_markup=markup)


async def get_diary(message: types.Message):
    """Получаем Дневник"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(buy, sell)
    markup.add(menu, all_notes)

    # Отправляем сообщение пользователю
    await message.answer("Это ваш дневник. Добавте покупку или продажу", reply_markup=markup)


async def cancel_state_send(message: types.Message, state: FSMContext):

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(buy, sell)
    markup.add(menu, all_notes)

    # Завершаем состояние и освобождаем память
    await state.finish()

    await message.answer('Отменено', reply_markup=markup)


async def gbuy(message: types.Message):
    """Делаем покупку Стадия 1"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    # Запуск состояния в котором будет формироваться переменные со значениями полученные от пользователя в ходе диалога
    await Buy.next()

    # Отправляем сообщение пользователю
    await message.answer("Введите пожалуйста сумму USDT (целое число)", reply_markup=markup)


async def gbuy_coin(message: types.Message, state: FSMContext):
    """Делаем покупку Стадия 2"""

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    if message.text == cancel_send:
        await cancel_state_send(message, state)
    else:
        # Формируем клавиатуру
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(cancel_send)

        # Проверяем является ли числом значение, которое передал пользователь
        if not is_int_or_float(message.text):
            await message.answer("Ошибка. Можно ввести только целые числа", reply_markup=markup)
            await state.finish()
            await get_diary(message)
        else:
            # Записываем в переменную amount (колличество) полученное значение от пользователя и сохраняем в памяти
            await state.update_data(amount=message.text)

            # Запуск состояния в котором будет формироваться переменные со значениями полученные от пользователя в ходе диалога
            await Buy.next()

            # Отправляем сообщение пользователю
            await message.answer("Введите пожалуйста имя монеты. Пример: BTCUSDT, ETHUSDT", reply_markup=markup)


async def gbuy_amount(message: types.Message, state: FSMContext):
    """Делаем покупку Стадия 3"""

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    if message.text == cancel_send:
        await cancel_state_send(message, state)
    else:
        # Формируем клавиатуру
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(cancel_send)

        # Проверяем является ли числом значение, которое передал пользователь
        if not BTCUSDT_or_ETHUSDT(message.text):
            await message.answer("Ошибка. Можно ввести только BTCUSDT и ETHUSDT", reply_markup=markup)
            await state.finish()
            await get_diary(message)
        else:
            # Записываем в переменную coin (монета) полученное значение от пользователя и сохраняем в памяти
            await state.update_data(coin=message.text)

            # Переходим к следующему циклу состояния
            await Buy.next()

            # Отправляем сообщение пользователю
            await message.answer("Введите цену покупки (целое число)", reply_markup=markup)


async def gbuy_price(message: types.Message, state: FSMContext):
    """Делаем покупку Стадия финал"""

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    if message.text == cancel_send:
        await cancel_state_send(message, state)
    else:
         # Формируем клавиатуру
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(buy, sell)
        markup.add(menu, all_notes)

        # Проверяем является ли числом значение, которое передал пользователь
        if not is_int_or_float(message.text):
            await message.answer("Ошибка. Можно ввести только целые числа", reply_markup=markup)
            await state.finish()
            await get_diary(message)
        else:
            # Записываем в переменную price (стоимость) полученное значение от пользователя и сохраняем в памяти
            await state.update_data(price=message.text)
            
            # Делаем обращение к памяти состояния для получения переменных, которые были записаны в ходе диалога бота с пользователем
            data = await state.get_data()
            
            # Получаем ID пользователя из диалога
            cid = message.chat.id

            # Формируем переменные из памяти состояния
            amount_usdt = data["amount"]
            amount_usdt = "%.2f" % float(amount_usdt)

            coin = data["coin"]
            price = data["price"]

            amount_coin = float(amount_usdt) / float(price)
            amount_coin = "%.2f" % float(amount_coin)

            # Формируем дату когда мы создаем покупку
            dt = datetime.now()
            timestamp = datetime.timestamp(dt)

            # Делаем запись в базу данных
            new_note = dict(cid=cid, coin=coin, amount_usdt=amount_usdt, amount_coin=amount_coin, price=price, side="Покупка", timestamp=timestamp)
            db_diary.insert_one(new_note)

            # Получаем баланс пользователя из базы данных
            user_balance = db_users.find_one({"cid": cid})

            if coin == "BTCUSDT":
                # Вычисляем новый баланс
                new_balance_usdt = float(user_balance["usdt"]) - float(amount_usdt)
                new_balance_coin = float(user_balance["btc"]) + float(amount_coin)
                # Делаем обновление баланса пользователя в базе данных
                db_users.update_one({"cid" : cid},{"$set":{"usdt": new_balance_usdt, "btc": new_balance_coin}})
            elif coin == "ETHUSDT":
                # Вычисляем новый баланс
                new_balance_usdt = float(user_balance["usdt"]) - float(amount_usdt)
                new_balance_coin = float(user_balance["eth"]) + float(amount_coin)
                # Делаем обновление баланса пользователя в базе данных
                db_users.update_one({"cid" : cid},{"$set":{"usdt": new_balance_usdt, "eth": new_balance_coin}})

            # Завершаем состояние и освобождаем память
            await state.finish()

            # Отправляем сообщение пользователю
            await message.answer(f"Запись добавлена в базу данных\nМонета: {coin} Колличество купленых монет: {amount_coin} Цена: {price}", reply_markup=markup)


async def gsell(message: types.Message):
    """Делаем продажу Стадия 1"""

    # Формируем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    # Переходим к следующему циклу состояния
    await Sell.next()

    # Отправляем сообщение пользователю
    await message.answer("Введите пожалуйста колличество монет (целое число)", reply_markup=markup)


async def gsell_coin(message: types.Message, state: FSMContext):
    """Делаем продажу Стадия 2"""

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    if message.text == cancel_send:
        await cancel_state_send(message, state)
    else:
        # Формируем клавиатуру
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(cancel_send)

        # Проверяем является ли числом значение, которое передал пользователь
        if not is_int_or_float(message.text):
            await message.answer("Ошибка. Можно ввести только целые числа", reply_markup=markup)
            await state.finish()
            await get_diary(message)
        else:
            # Записываем в переменную amount (колличество) полученное значение от пользователя и сохраняем в памяти
            await state.update_data(amount=message.text)

            # Запуск состояния в котором будет формироваться переменные со значениями полученные от пользователя в ходе диалога
            await Sell.next()

            # Отправляем сообщение пользователю
            await message.answer("Введите пожалуйста имя монеты. Пример: BTCUSDT. Внимание! Доступны монеты BTCUSDT, ETHUSDT", reply_markup=markup)


async def gsell_amount(message: types.Message, state: FSMContext):
    """Делаем продажу Стадия 3"""

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    if message.text == cancel_send:
        await cancel_state_send(message, state)
    else:
        # Формируем клавиатуру
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(cancel_send)

        # Проверяем является ли числом значение, которое передал пользователь
        if not BTCUSDT_or_ETHUSDT(message.text):
            await message.answer("Ошибка. Можно ввести только BTCUSDT и ETHUSDT", reply_markup=markup)
            await state.finish()
            await get_diary(message)
        else:
            # Записываем в переменную amount (колличество) полученное значение от пользователя и сохраняем в памяти
            await state.update_data(coin=message.text)

            # Переходим к следующему циклу состояния
            await Sell.next()

            # Отправляем сообщение пользователю
            await message.answer("Введите цену продажи (целое число)", reply_markup=markup)


async def gsell_price(message: types.Message, state: FSMContext):
    """Делаем продажу Стадия 4"""

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(cancel_send)

    if message.text == cancel_send:
        await cancel_state_send(message, state)
    else:
        # Формируем клавиатуру
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(buy, sell)
        markup.add(menu, all_notes)

        # Проверяем является ли числом значение, которое передал пользователь
        if not is_int_or_float(message.text):
            await message.answer("Ошибка. Можно ввести только целые числа", reply_markup=markup)
            await state.finish()
            await get_diary(message)
        else:
            # Записываем в переменную price (стоимость) полученное значение от пользователя и сохраняем в памяти
            await state.update_data(price=message.text)
            
            # Делаем обращение к памяти состояния для получения переменных, которые были записаны в ходе диалога бота с пользователем
            data = await state.get_data()
            
            # Формируем переменные из памяти состояния
            amount_coin = data["amount"]
            amount_coin = "%.2f" % float(amount_coin)

            coin = data["coin"]
            price = data["price"]
            
            amount_usdt = float(amount_coin) * float(price)
            amount_usdt = "%.2f" % float(amount_usdt)

            # Формируем дату когда мы создаем покупку
            dt = datetime.now()
            timestamp = datetime.timestamp(dt)

            # Получаем ID пользователя из диалога
            cid = message.chat.id

            # Делаем запись в базу данных
            new_note = dict(cid=cid, coin=coin, amount_usdt=amount_usdt, amount_coin=amount_coin, price=price, side="Продажа", timestamp=timestamp)
            db_diary.insert_one(new_note)

            # Получаем баланс пользователя из базы данных
            user_balance = db_users.find_one({"cid": cid})

            if coin == "BTCUSDT":
                # Вычисляем новый баланс
                new_balance_usdt = float(user_balance["usdt"]) + float(amount_usdt)
                new_balance_coin = float(user_balance["btc"]) - float(amount_coin)
                # Делаем обновление баланса пользователя в базе данных
                db_users.update_one({"cid" : cid},{"$set":{"usdt": new_balance_usdt, "btc": new_balance_coin}})
            elif coin == "ETHUSDT":
                # Вычисляем новый баланс
                new_balance_usdt = float(user_balance["usdt"]) + float(amount_usdt)
                new_balance_coin = float(user_balance["eth"]) - float(amount_coin)
                # Делаем обновление баланса пользователя в базе данных
                db_users.update_one({"cid" : cid},{"$set":{"usdt": new_balance_usdt, "eth": new_balance_coin}})

            # Завершаем состояние и освобождаем память
            await state.finish()
            
            # Отправляем сообщение пользователю
            await message.answer(f"Запись добавлена в базу данных\nМонета: {coin} Колличество проданых монет: {amount_coin} Цена: {price}", reply_markup=markup)


# Функция обработки запросов
def register_commands(dp: Dispatcher):
    """В данной функции обрабатываем запросы и запускаем необходимую функцию согласно запросу"""

    # Функция register_message_handler - зарезервированная функция в библиотеке, которую мы используем для реализции бота

    dp.register_message_handler(cmd_start, commands="start") # Пришла команда /start запускаем функцию cmd_start
    dp.register_message_handler(get_balance, text=balance) # Пришел в диалог текст 💰 Баланс запускаем функцию get_balance
    dp.register_message_handler(get_portfolio, text=portfolio)
    dp.register_message_handler(get_course, text=course)
    dp.register_message_handler(get_diary, text=diary)
    dp.register_message_handler(get_all_diary, text=all_notes)
    dp.register_message_handler(cmd_start_menu, text=menu)
   
    dp.register_message_handler(gbuy, text=buy)
    dp.register_message_handler(gbuy_coin, state=Buy.coin)
    dp.register_message_handler(gbuy_amount, state=Buy.amount)
    dp.register_message_handler(gbuy_price, state=Buy.price)

    dp.register_message_handler(gsell, text=sell)
    dp.register_message_handler(gsell_coin, state=Sell.coin)
    dp.register_message_handler(gsell_amount, state=Sell.amount)
    dp.register_message_handler(gsell_price, state=Sell.price)

    dp.register_message_handler(cancel_state_send, text=cancel_send)

    dp.register_message_handler(setting_user, text=setting)
    dp.register_message_handler(reset_user, text=reset)
    
