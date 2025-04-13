#!/usr/bin/env python3
# encoding: utf-8

import os
import json
import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from yandex_calendar_events2 import YandexCalendarEvents

# Загрузка переменных окружения из файла .env (если есть)
load_dotenv()

# Получение данных аутентификации из переменных окружения
CALDAV_URL = os.getenv("YANDEX_CALDAV_URL", "https://caldav.yandex.ru")
USERNAME = os.getenv("YANDEX_USERNAME")
PASSWORD = os.getenv("YANDEX_PASSWORD")

# Инициализация FastMCP сервера
mcp = FastMCP("yandex-calendar")

# Создание экземпляра класса YandexCalendarEvents
calendar_event = YandexCalendarEvents(
    caldav_url=CALDAV_URL,
    username=USERNAME,
    password=PASSWORD
)

@mcp.tool()
async def get_upcoming_events(days: int = 90, format_type: str = "text", ctx: Context = None) -> str:
    """
    Получить предстоящие события из Яндекс Календаря.

    Args:
        days (int): Количество дней для просмотра предстоящих событий. 
                    По умолчанию: 90.
        format_type (str): Формат вывода: "text" или "json".
                    По умолчанию: "text".
        ctx (Context): Контекст MCP, предоставляемый автоматически.

    Returns:
        str: Форматированный текст или JSON с предстоящими событиями, или сообщение об ошибке.
    """
    if ctx:
        ctx.info(f"Получение предстоящих событий за {days} дней")
    
    if not calendar_event.caldav_calendar:
        error_msg = "Ошибка: не удалось подключиться к Яндекс Календарю. Проверьте учетные данные."
        if ctx:
            ctx.error(error_msg)
        return error_msg
    
    events_text = await calendar_event.get_upcoming_events(days)
    
    # Если запрошен JSON формат, попробуем преобразовать текстовый вывод в JSON
    if format_type.lower() == "json" and events_text != "Нет предстоящих событий" and not events_text.startswith("Ошибка"):
        try:
            events_list = []
            # Разделяем события (каждое событие начинается с эмодзи календаря)
            raw_events = events_text.split("📅 ")
            
            for raw_event in raw_events:
                if not raw_event.strip():
                    continue
                    
                event_data = {}
                lines = raw_event.strip().split("\n")
                
                # Первая строка - название события
                event_data["title"] = lines[0].strip()
                
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith("Начало:"):
                        event_data["start"] = line.replace("Начало:", "").strip()
                    elif line.startswith("Окончание:"):
                        event_data["end"] = line.replace("Окончание:", "").strip()
                    elif line.startswith("Описание:"):
                        event_data["description"] = line.replace("Описание:", "").strip()
                
                events_list.append(event_data)
            
            return json.dumps({"events": events_list}, ensure_ascii=False, indent=2)
        except Exception as e:
            if ctx:
                ctx.error(f"Ошибка при преобразовании в JSON: {str(e)}")
            return events_text
    
    return events_text


@mcp.tool()
async def create_calendar_event(
    title: str, 
    start_date: str, 
    start_time: str, 
    duration_minutes: int = 60, 
    description: str = "", 
    ctx: Context = None
) -> str:
    """
    Запланировать новое событие в Яндекс Календаре.

    Args:
        title (str): Название события.
        start_date (str): Дата начала события в формате ДД.ММ.ГГГГ (например, 15.05.2025).
        start_time (str): Время начала события в формате ЧЧ:ММ (например, 14:30).
        duration_minutes (int): Продолжительность события в минутах. По умолчанию: 60 минут.
        description (str): Описание события. По умолчанию: пустая строка.
        ctx (Context): Контекст MCP, предоставляемый автоматически.

    Returns:
        str: Сообщение о результате создания события.
    """
    if ctx:
        ctx.info(f"Попытка создания события: {title} на {start_date} {start_time}")
    
    if not calendar_event.caldav_calendar:
        error_msg = "Ошибка: не удалось подключиться к Яндекс Календарю. Проверьте учетные данные."
        if ctx:
            ctx.error(error_msg)
        return error_msg
    
    try:
        # Преобразование строк даты и времени в datetime
        try:
            day, month, year = map(int, start_date.split('.'))
            hour, minute = map(int, start_time.split(':'))
            
            start = datetime.datetime(year, month, day, hour, minute)
            end = start + datetime.timedelta(minutes=duration_minutes)
            
        except ValueError as e:
            error_msg = f"Ошибка формата даты или времени: {str(e)}. Используйте формат ДД.ММ.ГГГГ для даты и ЧЧ:ММ для времени."
            if ctx:
                ctx.error(error_msg)
            return error_msg
        
        # Создание события
        result = await calendar_event.create_event(title, start, end, description)
        
        if ctx:
            if "успешно" in result:
                ctx.info(result)
            else:
                ctx.error(result)
        
        return result
        
    except Exception as e:
        error_msg = f"Ошибка при создании события: {str(e)}"
        if ctx:
            ctx.error(error_msg)
        return error_msg

if __name__ == "__main__":
    mcp.run(transport='stdio')
