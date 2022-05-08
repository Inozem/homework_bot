import time

import requests
import telegram



PRACTICUM_TOKEN = "AQAAAAAVr9FqAAYckWCB_5FF5UOTjbwIA0BOhQM"
TELEGRAM_TOKEN = '5396406850:AAEgbULT3rcNM18oe7a1o5cjfIzLwqTiC7w'
TELEGRAM_CHAT_ID = 499171407

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


LAST_HOMEWORK_STATUS = ''


def send_message(bot, message):
    pass


def get_api_answer(current_timestamp):
    """Делаем API запрос"""
    timestamp = 0
    params = {'from_date': timestamp}
    return requests.get(ENDPOINT, headers=HEADERS, params=params).json()


def check_response(response):
    """Проверяем тип данных API"""
    if type(response) == dict:
        return (response['homeworks'])
    else:
        print('Неверный формат данных API')
        return None


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
    current_timestamp = 0

    api_answer = get_api_answer(current_timestamp)


    try:
        response = check_response(api_answer)

        print(response)
        print(api_answer['current_date'])
        print(current_timestamp)

    except Exception as error:
        print(f'Сбой в работе программы: {error}')




if __name__ == '__main__':
    main()
