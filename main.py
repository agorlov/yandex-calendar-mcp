#!/usr/bin/env python3
# encoding: utf-8

import httpx
import re
import datetime
import sys
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from yandex_calendar_events import YandexCalendarEvents

# Инициализация FastMCP сервера
mcp = FastMCP("yandex-calendar")

# Глобальная переменная для хранения URL календаря
# Если URL передан как аргумент командной строки, используем его
CALENDAR_URL = sys.argv[1] if len(sys.argv) > 1 else ""

# Создание экземпляра класса YandexCalendarEvents
calendar_event = YandexCalendarEvents(CALENDAR_URL)

@mcp.tool()
async def get_upcoming_events(days: int = 90) -> str:
    """
    Получить предстоящие события из Яндекс Календаря.

    Args:
        days (int): Количество дней для просмотра предстоящих событий. 
                    По умолчанию: 90.

    Returns:
        str: Форматированный текст с предстоящими событиями или сообщение об ошибке.
    """
    return await calendar_event.get_upcoming_events(days)

if __name__ == "__main__":
    mcp.run(transport='stdio')
