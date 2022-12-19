
## Описание

Телеграм бот для криптовалютного инвестора.

Описание проекта: 3 функции - БАЛАНС, ПОРТФЕЛЬ, ДНЕВНИК, КУРС

`БАЛАНС` - показывает общий баланс по монетам пользователя и их среднюю цену

`КУРС` - показывает цену зарегистрированных монет и % изменение цены за 24 часа

`ДНЕВНИК` - ведёт для каждого человека дневник его покупок и продаж (историю сделок). Пользователь может добавить покупку или продажу монеты 

`ПОРТФЕЛЬ` - показывает все зарегистрированные монеты в боте

## Установка утилит и настройка сервера

Обновляем систему

```
sudo apt update
```

```
apt install python3 -y
```

```
apt install python3-pip -y
```

```
pip3 install pymongo
```

```
pip3 install aiogram
```


## Установка mongodb

```
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

```

```
sudo apt-get install gnupg

```

```
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

```

```
echo "deb http://security.ubuntu.com/ubuntu focal-security main" | sudo tee /etc/apt/sources.list.d/focal-security.list

```

```
sudo apt update
```

```
sudo apt-get install libssl1.1
```

```
sudo apt-get install -y mongodb-org

```

```
sudo systemctl daemon-reload
```

```
sudo systemctl start mongod
```

```
sudo systemctl enable mongod
```

## Запуск

```
apt install screen -y
```
 
Запускаем утилиту screen для запуска бота в фоне `После запуска нажмите Enter`
```
screen 
```

Запустить бота
```
python3 app.py
```
