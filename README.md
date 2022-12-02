# Телеграм бот Яндекс.Домашка 

## Описание проекта

Телеграм бот написанный с помощью билиотеки **python-telegram-bot** для мониторинга статуса домашних работ на Яндекс.Практикум.

Бот: 
- раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
 - при обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram;
- логирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.

## Требования

Чтобы пользоваться ботом, вы должны быть студентом Яндекс.Практикум. Перед устанвокой проекта необходимо подписатсья на сам бот: https://t.me/practicum_homework_status_robot

Для наполнения .env файла потребуется:
1. Получить oAuth токен по ссылке: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a

2. Узнать свой Chat ID. Для этого достаточно подписться на Telegram бота https://t.me/userinfobot и отправаить ему свой логин. Бот ответным сообщением отправит ваш Chat ID.


## Установка проекта из репозитория и запуск (Linux и macOS)

1. Клонировать репозиторий 

```bash
git clone git@github.com:FinkTim/homework_bot.git
```

2. Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv

source venv/bin/activate
```

3. Установить зависимости из файла ```requirements.txt```:

```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

4. Запустить скрипт:

```bash
python3 homework.py
```

## Шаблон наполнения .env файла  

```sh
PRACTICUM_TOKEN = 'xx_XxXXXXXXxxxlAAYckQXXXXXDVjqd5RHMITneLQ3iHWFDQtheN_GnI2vY'
TELEGRAM_CHAT_ID = 0123456789
```

# Авторы

* [Shandalii Dmitrii](https://github.com/FinkTim)
