from datetime import datetime, timedelta

import requests

url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {
    'Authorization': f'OAuth {"AQAAAAAVr9FqAAYckWCB_5FF5UOTjbwIA0BOhQM"}'
}

days_ago = 1
from_date = int((datetime.now() - timedelta(days=days_ago)).timestamp())
payload = {'from_date': from_date}

homework_statuses = requests.get(url, headers=headers, params=payload)

print(homework_statuses.text)
print(homework_statuses.json())
