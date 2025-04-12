# yandex_calendar_events.py

import httpx
import re
import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

class YandexCalendarEvents:
    def __init__(self, calendar_url: str):
        self.calendar_url = calendar_url

    def _parse_datetime(self, date_str: str) -> Optional[datetime.datetime]:
        """Парсинг даты из формата Яндекс Календаря"""
        if not date_str:
            return None
        
        # Соответствие русских названий месяцев номерам
        months_ru = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }
        
        try:
            # Извлечение компонентов из строки даты
            match = re.match(r'(\d+)\s+(\w+)\s+(\d+)\s+(\d+):(\d+)', date_str)
            if match:
                day, month_name, year, hour, minute = match.groups()
                month_num = months_ru.get(month_name.lower())
                if month_num:
                    return datetime.datetime(
                        int(year), month_num, int(day), int(hour), int(minute)
                    )
            return None
        except (ValueError, TypeError):
            return None

    def _parse_calendar_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Парсинг HTML содержимого из Яндекс Календаря"""
        soup = BeautifulSoup(html_content, 'html.parser')
        events = []
        
        for event_div in soup.select('.b-content-event'):
            # Извлечение данных о событии
            title = event_div.h1.text.strip() if event_div.h1 else "Без названия"
            
            # Извлечение временных интервалов
            time_spans = event_div.select('.e-time span')
            if len(time_spans) >= 2:
                start_time = time_spans[0].text.strip()
                end_time = time_spans[1].text.strip()
            else:
                start_time = time_spans[0].text.strip() if time_spans else "Неизвестное время"
                end_time = None
            
            # Парсинг даты и времени начала/конца
            start_dt = self._parse_datetime(start_time)
            end_dt = self._parse_datetime(end_time) if end_time else None
            
            # Создание словаря события
            event = {
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "start_datetime": start_dt,
                "end_datetime": end_dt
            }
            
            events.append(event)
        
        # Сортировка событий по времени начала
        events.sort(key=lambda x: x["start_datetime"] if x["start_datetime"] else datetime.datetime.max)
        
        return events

    async def get_upcoming_events(self, days: int = 90) -> str:
        """
        Получить предстоящие события из Яндекс Календаря.
        
        Args:
            days (int): Количество дней для просмотра предстоящих событий. 
                        По умолчанию: 90.

        Returns:
            str: Форматированный текст с предстоящими событиями или сообщение об ошибке.
                  Пример возвращаемого значения:
                  
                  # Предстоящие события (ближайшие 90 дней)
                  ## Понедельник, 14 апреля 2025
                  ### Название события
                  * Время: 10:00 - 11:00
                  * Время: 12:00 - 13:00
                  ## Вторник, 15 апреля 2025
                  ### Название другого события
                  * Время: 14:00 - 15:00
        """
        if not self.calendar_url:
            return "URL календаря не установлен."

        # Загрузка данных календаря
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.calendar_url)
                response.raise_for_status()
                html_content = response.text
        except Exception as e:
            return f"Ошибка при загрузке календаря: {str(e)}"

        # Парсинг событий
        events = self._parse_calendar_html(html_content)

        # Фильтрация событий на предстоящие дни
        now = datetime.datetime.now()
        end_date = now + datetime.timedelta(days=days)

        upcoming_events = [
            event for event in events 
            if event["start_datetime"] and now <= event["start_datetime"] <= end_date
        ]

        if not upcoming_events:
            return f"Нет предстоящих событий в ближайшие {days} дней."

        # Форматирование событий в текст
        result = f"# Предстоящие события (ближайшие {days} дней)\n\n"
        
        # Группировка событий по дате
        events_by_date = {}
        for event in upcoming_events:
            event_date = event["start_datetime"].date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Форматирование событий по датам
        for date in sorted(events_by_date.keys()):
            # Форматирование даты как "Понедельник, 14 апреля 2025"
            date_str = date.strftime("%A, %d %B %Y")
            result += f"## {date_str}\n\n"
            
            # Сортировка событий по времени начала
            day_events = sorted(events_by_date[date], key=lambda x: x["start_datetime"])
            
            for event in day_events:
                start_time = event["start_datetime"].strftime("%H:%M")
                end_time = event["end_datetime"].strftime("%H:%M") if event["end_datetime"] else "N/A"
                
                result += f"### {event['title']}\n"
                result += f"* Время: {start_time} - {end_time}\n\n"
        
        return result