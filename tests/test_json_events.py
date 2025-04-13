#!/usr/bin/env python3
# encoding: utf-8

"""
Тест получения событий в формате JSON и удаления события

Этот тест демонстрирует:
1. Получение списка предстоящих событий в формате JSON
2. Красивый вывод JSON для анализа структуры данных
3. Интерактивный процесс выбора события для удаления
4. Демонстрацию удаления события по его UID
5. Проверку результатов удаления

Тест особенно полезен для:
- Изучения структуры JSON-ответа календаря
- Проверки работы удаления событий
- Понимания формата идентификаторов событий
"""

import os
import sys
import json
import asyncio
import datetime
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yandex_calendar_events2 import YandexCalendarEvents

# Загрузка переменных окружения из файла .env (если есть)
load_dotenv()

# Получение данных аутентификации из переменных окружения
CALDAV_URL = os.getenv("YANDEX_CALDAV_URL", "https://caldav.yandex.ru")
USERNAME = os.getenv("YANDEX_USERNAME")
PASSWORD = os.getenv("YANDEX_PASSWORD")

async def main():
    print("Инициализация подключения к Яндекс Календарю...")
    # Создание экземпляра класса YandexCalendarEvents
    calendar = YandexCalendarEvents(
        caldav_url=CALDAV_URL,
        username=USERNAME,
        password=PASSWORD
    )
    
    if not calendar.caldav_calendar:
        print("Ошибка: не удалось подключиться к Яндекс Календарю")
        return
    
    print("\n1. Получение списка событий на следующие 7 дней в формате JSON...")
    events_result = await calendar.get_upcoming_events(days=7, format_type="json")
    
    # Вывод результата в консоль в красивом формате
    print(json.dumps(events_result, ensure_ascii=False, indent=2))
    
    # Если есть события, выберем первое для тестового удаления
    if isinstance(events_result, dict) and events_result.get("count", 0) > 0:
        first_event = events_result["events"][0]
        event_uid = first_event.get("uid")
        event_title = first_event.get("title")
        
        if event_uid:
            print(f"\n2. Выбрано событие для тестирования удаления:")
            print(f"   Название: {event_title}")
            print(f"   UID: {event_uid}")
            
            confirm = input("\nВы действительно хотите удалить это событие? (да/нет): ")
            
            if confirm.lower() == "да":
                print("\n3. Удаление тестового события...")
                result = await calendar.delete_event(event_uid)
                print(f"   Результат: {result}")
                
                # Получение обновленного списка событий
                print("\n4. Получение обновленного списка событий...")
                updated_events = await calendar.get_upcoming_events(days=7, format_type="json")
                
                # Проверка, что событие было удалено
                found = False
                for event in updated_events.get("events", []):
                    if event.get("uid") == event_uid:
                        found = True
                        break
                
                if not found:
                    print("   Событие успешно удалено из календаря!")
                else:
                    print("   Ошибка: событие по-прежнему присутствует в календаре.")
            else:
                print("Удаление отменено.")
        else:
            print("Не удалось получить UID события для тестирования удаления.")
    else:
        print("Нет доступных событий для тестирования удаления.")

if __name__ == "__main__":
    asyncio.run(main())
