import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (HomeworkStatusError, ResponseStatusError,
                        TelegramMessageSendError)

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('main.log')
    ]
)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message: str) -> None:
    """Отправляем сообщение с API."""
    logging.info('Начинаем отправку сообщения')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        raise TelegramMessageSendError('Сообщение не отправлено')
    else:
        logging.info(f'Успешно отправлено сообщение: {message}')


def get_api_answer(current_timestamp: int) -> dict:
    """Обращаемся к эндпоинту API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logging.info(
            f'Начало запроса к API с параметрами:{params, HEADERS, ENDPOINT}')
        if response.status_code != HTTPStatus.OK:
            raise ResponseStatusError('Код ответа сервера не 200')
        return response.json()
    except Exception:
        raise Exception('Ошибка при запросе к API')


def check_response(response: dict) -> list:
    """Проверяем ответ на соответствие требованиям."""
    if not isinstance(response, dict):
        raise TypeError('В качестве аргумента передан не словарь')
    homeworks = response.get('homeworks')
    current_date = response.get('current_date')
    if homeworks is None or current_date is None:
        raise KeyError('Ключи в ответе API не соответсвуют ожидаемым')
    if not isinstance(homeworks, list):
        raise TypeError('В списке домашних работ неверный тип данных')
    return homeworks


def parse_status(homework: dict) -> str:
    """Парсим статус домашки."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if not homework_name:
        raise KeyError('Пустое значение.')
    if homework_status not in HOMEWORK_STATUSES:
        message = 'Недокументированный статус домашней работы.'
        raise HomeworkStatusError(message)
    verdict = HOMEWORK_STATUSES[homework_status]
    logging.info('Обновлен статус проверки работы.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяем доступность токенов в окружении проекта."""
    TOKENS = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    return all(TOKENS)


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        logging.critical('Отсутствует переменная окружения')
        sys.exit('Бот завершил работу')

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                status = parse_status(homeworks[0])
                send_message(bot, status)
            current_timestamp = response['current_date']
        except TelegramMessageSendError:
            logging.error('Ошибка отправки сообщения в Telegram')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
