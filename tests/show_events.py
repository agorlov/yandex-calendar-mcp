"""
Просмотр событий на следующую неделю

Этот скрипт демонстрирует базовую функциональность для просмотра
предстоящих событий в Яндекс Календаре. Он показывает:
1. Поиск событий на следующую неделю
2. Форматирование и отображение найденных событий с датами
3. Корректную обработку случая, когда нет событий

Полезно для быстрой проверки подключения к календарю и 
просмотра запланированных событий.
"""

import asyncio
import datetime
import os
import sys
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yandex_calendar_events2 import YandexCalendarEvents

async def main():
    # Загрузка переменных окружения из файла .env
    load_dotenv()
    
    # Получение учетных данных из переменных окружения
    CALDAV_BASE_URL = os.getenv("YANDEX_CALDAV_URL", "https://caldav.yandex.ru")
    USERNAME = os.getenv("YANDEX_USERNAME")
    PASSWORD = os.getenv("YANDEX_PASSWORD")
    
    if not USERNAME or not PASSWORD:
        print("Ошибка: Учетные данные не найдены. Проверьте переменные окружения YANDEX_USERNAME и YANDEX_PASSWORD")
        return
    
    calendar = YandexCalendarEvents(
        caldav_url=CALDAV_BASE_URL,
        username=USERNAME,
        password=PASSWORD
    )
    
    if not calendar.caldav_calendar:
        print("Не удалось подключиться к CalDAV")
        return

    # Получаем даты начала и конца следующей недели
    today = datetime.datetime.now()
    days_until_next_monday = (7 - today.weekday()) % 7
    next_monday = today + datetime.timedelta(days=days_until_next_monday)
    next_sunday = next_monday + datetime.timedelta(days=6)
    
    print(f"\nСобытия на следующую неделю ({next_monday.strftime('%d.%m.%Y')} - {next_sunday.strftime('%d.%m.%Y')}):")
    try:
        events = calendar.caldav_calendar.date_search(
            start=next_monday,
            end=next_sunday + datetime.timedelta(days=1))
        
        if not events:
            print("Нет запланированных событий на следующую неделю")
            return
            
        for event in events:
            summary = event.instance.vevent.summary.value
            start_date = event.instance.vevent.dtstart.value
            if isinstance(start_date, datetime.date) and not isinstance(start_date, datetime.datetime):
                start_date = datetime.datetime.combine(start_date, datetime.time())
            print(f"- {start_date.strftime('%d.%m.%Y %H:%M')} : {summary}")
            
    except Exception as e:
        print(f"Ошибка при получении событий: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())