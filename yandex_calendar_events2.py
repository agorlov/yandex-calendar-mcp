import httpx
import re
import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import caldav
from caldav.elements import dav

class YandexCalendarEvents:
    def __init__(self, caldav_url: str = None,
                 username: str = None, password: str = None):
        self.caldav_url = caldav_url
        self.username = username
        self.password = password
        self.caldav_client = None
        self.caldav_calendar = None
        if caldav_url and username and password:
            self._init_caldav()

    def _init_caldav(self):
        """Инициализация CalDAV клиента"""
        try:
            self.caldav_client = caldav.DAVClient(
                url=self.caldav_url,
                username=self.username,
                password=self.password
            )
            
            # Получаем principal (основной календарь)
            principal = self.caldav_client.principal()
            
            # Получаем все доступные календари
            calendars = principal.calendars()
            
            if not calendars:
                raise Exception("No calendars found")
                
            # Используем первый доступный календарь
            self.caldav_calendar = calendars[0]
            print(f"Successfully connected to calendar: {self.caldav_calendar.name}")
            
        except Exception as e:
            print(f"CalDAV Error: {str(e)}")
            self.caldav_client = None
            self.caldav_calendar = None



    async def create_event(self, title: str, start: datetime.datetime, 
                           end: datetime.datetime, description: str = "") -> str:
        """
        Создать новое событие через CalDAV
        """
        if not self.caldav_calendar:
            return "CalDAV не настроен"
            
        ical = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{title}
DESCRIPTION:{description}
UID:{datetime.datetime.now().timestamp()}@yandex.ru
END:VEVENT
END:VCALENDAR"""

        try:
            self.caldav_calendar.add_event(ical)
            return f"Событие '{title}' успешно создано"
        except Exception as e:
            return f"Ошибка создания события: {str(e)}"

    async def delete_event(self, event_uid: str) -> str:
        """
        Удалить событие по UID
        """
        if not self.caldav_calendar:
            return "CalDAV не настроен"
            
        try:
            # Получаем событие напрямую по UID
            event = self.caldav_calendar.object_by_uid(event_uid)
            if event:
                event.delete()
                return f"Событие {event_uid} удалено"
            return "Событие не найдено"
        except Exception as e:
            return f"Ошибка удаления: {str(e)}"

    async def get_upcoming_events(self, days: int = 90) -> str:
        """
        Получить предстоящие события из календаря
        
        Args:
            days (int): Количество дней для просмотра предстоящих событий
            
        Returns:
            str: Форматированный текст со списком событий или сообщение об ошибке
        """
        if not self.caldav_calendar:
            return "CalDAV не настроен"
            
        try:
            # Вычисляем даты начала и конца периода
            start = datetime.datetime.now()
            end = start + datetime.timedelta(days=days)
            
            # Получаем события за указанный период
            events = self.caldav_calendar.date_search(
                start=start,
                end=end
            )
            
            if not events:
                return "Нет предстоящих событий"
            
            # Форматируем вывод событий
            result = []
            for event in events:
                event_data = event.data
                event_lines = event_data.split('\n')
                
                # Извлекаем основные данные события
                summary = None
                start_date = None
                end_date = None
                description = None
                
                for line in event_lines:
                    if line.startswith('SUMMARY:'):
                        summary = line.replace('SUMMARY:', '')
                    elif line.startswith('DTSTART'):
                        date_str = line.split(':')[1]
                        # Преобразуем дату из формата YYYYMMDDTHHMMSS
                        start_date = datetime.datetime.strptime(date_str[:15], '%Y%m%dT%H%M%S')
                    elif line.startswith('DTEND'):
                        date_str = line.split(':')[1]
                        end_date = datetime.datetime.strptime(date_str[:15], '%Y%m%dT%H%M%S')
                    elif line.startswith('DESCRIPTION:'):
                        description = line.replace('DESCRIPTION:', '')
                
                if summary and start_date:
                    event_str = f"📅 {summary}\n"
                    event_str += f"   Начало: {start_date.strftime('%d.%m.%Y %H:%M')}\n"
                    if end_date:
                        event_str += f"   Окончание: {end_date.strftime('%d.%m.%Y %H:%M')}\n"
                    if description:
                        event_str += f"   Описание: {description}\n"
                    result.append(event_str)
            
            return "\n".join(result) if result else "Нет предстоящих событий"
            
        except Exception as e:
            return f"Ошибка при получении событий: {str(e)}"
