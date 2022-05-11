import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

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
TELEGRAM_CHAT_ID = 499171407

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

LAST_MESSAGE = ''

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class GetApiAnswerError(Exception):
    """Класс ошибки ответа API."""

    pass


def send_message(bot, message):
    """Отправка сообщения."""
    global LAST_MESSAGE
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
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        error_message = 'Возникли проблемы с запросом API'
        logger.error(error_message)
        raise GetApiAnswerError(error_message)


def check_response(response):
    """Проверяем тип данных API."""
    if type(response) == dict:
        homeworks = response['homeworks']
        if type(homeworks) != list:
            error_message = 'Неверный тип данных домашних работ'
            logger.error(error_message)
            raise TypeError(error_message)
        try:
            return (homeworks)
        except KeyError:
            error_message = ('В запросе отутствует ключ "homeworks"')
            logger.error(error_message)
            raise KeyError(error_message)
        except Exception:
            error_message = 'Отсутствие ожидаемых ключей в ответе API'
            logger.error(error_message)
    else:
        error_message = 'Неверный тип данных API'
        logger.error(error_message)
        raise TypeError(error_message)


def parse_status(homework):
    """Проверяем статус домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        error_message = (f'Статус домашней работы "{homework_status}" '
                         'отсутствует в списке')
        logger.error(error_message)
        raise KeyError(error_message)
    except Exception:
        error_message = 'Отсутствует статус домашней работы'
        logger.error(error_message)


def check_tokens():
    """Проверка наличия токенов."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN:
        return True
    else:
        logger.critical('Отсутствует одна из обязательных переменных')
        return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return None

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            api_answer = get_api_answer(current_timestamp)
            response = check_response(api_answer)

            if response != []:
                status = parse_status(response[0])
                send_message(bot, status)
            else:
                logger.debug('Статус домашней работы не обновлен ревьюером')

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
