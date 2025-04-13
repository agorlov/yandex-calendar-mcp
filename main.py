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
async def get_upcoming_events(days: int = 90, format_type: str = "json", ctx: Context = None) -> str:
    """
    Получить предстоящие события из Яндекс Календаря.

    Args:
        days (int): Количество дней для просмотра предстоящих событий. 
                    По умолчанию: 90.
        format_type (str): Формат вывода: "text" или "json".
                    По умолчанию: "json".
        ctx (Context): Контекст MCP, предоставляемый автоматически.

    Returns:
        str: Форматированный текст или JSON с предстоящими событиями, или сообщение об ошибке.
    """
    if ctx:
        await ctx.info(f"Получение предстоящих событий за {days} дней в формате {format_type}")
    
    if not calendar_event.caldav_calendar:
        error_msg = "Ошибка: не удалось подключиться к Яндекс Календарю. Проверьте учетные данные."
        if ctx:
            await ctx.error(error_msg)
        return error_msg
    
    try:
        events_result = await calendar_event.get_upcoming_events(days, format_type)
        
        # Если результат уже строка, то возвращаем его
        if isinstance(events_result, str):
            return events_result
            
        # Если результат - словарь, то преобразуем его в JSON строку
        return json.dumps(events_result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"Ошибка при получении событий: {str(e)}"
        if ctx:
            ctx.error(error_msg)
        return error_msg


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
        await ctx.info(f"Попытка создания события: {title} на {start_date} {start_time}")
    
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
                await ctx.error(error_msg)
            return error_msg
        
        # Создание события
        result = await calendar_event.create_event(title, start, end, description)
        
        if ctx:
            if "успешно" in result:
                await ctx.info(result)
            else:
                await ctx.error(result)
        
        return result
        
    except Exception as e:
        error_msg = f"Ошибка при создании события: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return error_msg


@mcp.tool()
async def delete_calendar_event(event_uid: str, ctx: Context = None) -> str:
    """
    Удалить событие из Яндекс Календаря по его уникальному идентификатору.

    Args:
        event_uid (str): Уникальный идентификатор события (uid).
        ctx (Context): Контекст MCP, предоставляемый автоматически.

    Returns:
        str: Сообщение о результате удаления события.
    """
    if ctx:
        await ctx.info(f"Попытка удаления события с ID: {event_uid}")
    
    if not calendar_event.caldav_calendar:
        error_msg = "Ошибка: не удалось подключиться к Яндекс Календарю. Проверьте учетные данные."
        if ctx:
            ctx.error(error_msg)
        return error_msg
    
    try:
        result = await calendar_event.delete_event(event_uid)
        
        if ctx:
            if "успешно" in result:
                await ctx.info(result)
            else:
                await ctx.error(result)
        
        return result
        
    except Exception as e:
        error_msg = f"Ошибка при удалении события: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return error_msg

if __name__ == "__main__":
    mcp.run(transport='stdio')
