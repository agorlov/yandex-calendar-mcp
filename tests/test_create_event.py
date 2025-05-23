#!/usr/bin/env python3
# encoding: utf-8

"""
Тест создания события в Яндекс Календаре

Этот тест проверяет функциональность создания нового события:
1. Создает одно тестовое событие на завтра с заданным временем (15:00)
2. Устанавливает продолжительность события (1 час)
3. Добавляет описание события
4. Выводит результат операции создания события

"""

import os
import sys
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
    # Создание экземпляра класса YandexCalendarEvents
    calendar = YandexCalendarEvents(
        caldav_url=CALDAV_URL,
        username=USERNAME,
        password=PASSWORD
    )
    
    if not calendar.caldav_calendar:
        print("Ошибка: не удалось подключиться к Яндекс Календарю")
        return
    
    # Определение времени для тестового события
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    start = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0)  # Завтра в 15:00
    end = start + datetime.timedelta(hours=1)  # Продолжительность - 1 час
    
    print(f"Создание тестового события:")
    print(f"Название: Тестовое событие из MCP")
    print(f"Начало: {start.strftime('%d.%m.%Y %H:%M')}")
    print(f"Окончание: {end.strftime('%d.%m.%Y %H:%M')}")
    
    # Создание события
    result = await calendar.create_event(
        "Тестовое событие из MCP", 
        start, 
        end, 
        "Создано с помощью MCP сервера"
    )
    
    print(f"\nРезультат: {result}")

if __name__ == "__main__":
    asyncio.run(main())
