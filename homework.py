import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = 499171407

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Делаем API запрос"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    return requests.get(ENDPOINT, headers=HEADERS, params=params).json()


def check_response(response):
    """Проверяем тип данных API"""
    if type(response) == dict:
        return (response['homeworks'])
    else:
        print('Неверный формат данных API')
        return None


def parse_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия токенов"""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN:
        print('Токены получены')
        return True
    else:
        print('Отсутствует один из токенов')
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

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
            main()


if __name__ == '__main__':
    main()
