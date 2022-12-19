from lib.mdb import Mdb 
import sys 
import pymongo

# Тест 1: наличие пользователя в базе данных

from handlers.commands import is_int_or_float, BTCUSDT_or_ETHUSDT

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


# Тестируем получения пользователя 
def test_is_user(cid: str) -> str:

    is_user = mdb.is_user(cid)

    if not is_user:
        return print("Ошибка. Нет пользователя в базе")
    else:
        return print("Успех. Функция проверки пользователя в базе")

    
# Тест 2: проверка на цифры
def test_is_int_or_float(item:float) -> str:

    _float = is_int_or_float(item)

    if not _float:
        return print("Ошибка. Функция принимает только цифры")
    else:
        return print("Успех. Функция проверки на цифры")

# Тест 3: проверка на совпадение
def test_is_BTC_AND_ETH(coin:float) -> str:

    _is_coin = BTCUSDT_or_ETHUSDT(coin)

    if not _is_coin:
        return print("Ошибка. Функция принимает только BTCUSDT и ETHUSDT")
    else:
        return print("Успех. Функция проверки совпадения")

if __name__ == '__main__':
    # Создаем конструкцию try except для отловли исключения ошибок программы
    try:
        print("Тест запущен")
        print("--------------")
        # Проверка на успех
        test_is_user("184217209")
        test_is_int_or_float("3000")
        test_is_BTC_AND_ETH("BTCUSDT")

        print("------------------------")

        # Передача ошибочных значений и типов
        test_is_user("123456789")
        test_is_int_or_float("Вызов ошибки")
        test_is_BTC_AND_ETH("TONUSDT")

    except Exception as err:
        print(err) # Вывод ошибки 

   
