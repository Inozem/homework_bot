import logging
import os
import time
from logging.handlers import RotatingFileHandler
from sys import exit

import requests
import telegram
from dotenv import load_dotenv

from exceptions import GetApiAnswerError, NoneCriticalError

load_dotenv()

logging.basicConfig(
    format='%(asctime)s, %(levelname)s, %(message)s'
)

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

LAST_MESSAGE = ''

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения."""
    global LAST_MESSAGE
    logger.debug(f'Начало отправки сообщения "{message}"')
    try:
        if message != LAST_MESSAGE:
            bot.send_message(TELEGRAM_CHAT_ID, message)
            LAST_MESSAGE = message
            logger.info(message)
    except Exception as error:
        logger.error(f'Ошибка "{error}" при отправке '
                     f'сообщения "{message}" в Telegram')


def get_api_answer(current_timestamp):
    """Делаем API запрос."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    logger.debug(f'Начало отправки запроса с параметрами "{params}"')
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        error_message = ('Возникли проблемы с запросом API, '
                         f'статус запроса "{response.status_code}". '
                         f'headers = {HEADERS}, params = {params}')
        logger.error(error_message)
        raise GetApiAnswerError(error_message)


def check_response(response):
    """Проверяем тип данных API."""
    if not isinstance(response, dict):
        error_message = 'Неверный тип данных API'
        raise TypeError(error_message)
    elif 'homeworks' not in response:
        error_message = ('В запросе отутствует ключ "homeworks"')
        raise KeyError(error_message)
    elif not isinstance(response['homeworks'], list):
        error_message = ('Неверный тип данных домашних работ')
        raise TypeError(error_message)
    else:
        return response['homeworks']


def parse_status(homework):
    """Проверяем статус домашней работы."""
    if 'homework_name' not in homework:
        error_message = ('В домашней работе отутствует ключ "homework_name"')
        raise KeyError(error_message)
    elif 'status' not in homework:
        error_message = ('В домашней работе отутствует ключ "status"')
        raise KeyError(error_message)
    else:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия токенов."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    else:
        logger.critical('Отсутствует одна или несколько '
                        'обязательных переменных')
        return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_message = ('Отсутствует одна или несколько '
                         'обязательных переменных')
        logger.critical(error_message)
        exit('Отсутствует одна или несколько обязательных переменных')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            api_answer = get_api_answer(current_timestamp)
            response = check_response(api_answer)

            if response:
                status = parse_status(response[0])
                send_message(bot, status)
            else:
                error_message = 'Статус домашней работы не обновлен ревьюером'
                logger.debug(error_message)
                raise NoneCriticalError(error_message)
            current_timestamp = int(time.time())
        except NoneCriticalError as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
