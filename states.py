from aiogram.dispatcher.filters.state import StatesGroup, State

# Формируем классы состояний 
class Buy(StatesGroup):
    coin = State()
    amount = State()
    price = State()

class Sell(StatesGroup):
    coin = State()
    amount = State()
    price = State()
