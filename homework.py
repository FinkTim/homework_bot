import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import HomeworkStatusError, ResponseStatusError

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='w'
)

logger = logging.getLogger(__name__)
handler = StreamHandler(sys.stdout)
logger.addHandler(handler)

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


def send_message(bot, message):
    """Отправляем сообщение с API."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'В Telegram отправлено сообщение: {message}')
    except Exception as error:
        message = f'Сообщение не отправлено: {error}'
        logger.error(message)


def get_api_answer(current_timestamp):
    """Обращаемся к эндпоинту API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logger.info('Начало запроса к API')
        if response.status_code != HTTPStatus.OK:
            raise ResponseStatusError('Код ответа сервера не 200')
        return response.json()
    except ResponseStatusError:
        raise ResponseStatusError('Код ответа сервера не 200')
    except Exception as error:
        message = f'Ошибка при запросе к API: {error}'
        logger.error(message)


def check_response(response):
    """Проверяем ответ на соответствие требованиям."""
    homeworks = response['homeworks']
    if not isinstance(response, dict):
        logger.error('В ответе передан неверный тип данных')
        raise TypeError
    if 'homeworks' and 'current_date' not in response.keys():
        logger.error('Переданы неверные ключи в ответе API')
        raise KeyError
    if not isinstance(homeworks, list):
        logger.error('В списке домашних работ неверный тип данных')
        raise TypeError
    return homeworks


def parse_status(homework):
    """Парсим статус домашки."""
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_name is None:
        message = 'Пустое значение.'
        logger.error(message)
        raise HomeworkStatusError(message)
    if homework_status not in HOMEWORK_STATUSES:
        message = 'Недокументированный статус домашней работы.'
        logger.error(message)
        raise HomeworkStatusError(message)
    verdict = HOMEWORK_STATUSES[homework_status]
    logger.info('Обновлен статус проверки работы.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем доступность токенов в окружении проекта."""
    TOKENS = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(TOKENS)


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        logger.critical('Отсутствует переменная окружения')
        exit()

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if len(homeworks) != 0:
                status = parse_status(homeworks[0])
                send_message(bot, status)
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
