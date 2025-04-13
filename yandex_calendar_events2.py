import httpx
import re
import json
import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
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
            # Создаем клиента с учетными данными
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

    def _parse_ical_event(self, event_data: str) -> Dict[str, Any]:
        """
        Парсинг iCal данных события
        
        Args:
            event_data (str): Сырые данные события в формате iCal
            
        Returns:
            Dict[str, Any]: Словарь с данными события
        """
        event_dict = {}
        event_lines = event_data.split('\n')
        
        # Общие поля, которые мы хотим извлечь
        for line in event_lines:
            line = line.strip()
            if line.startswith('SUMMARY:'):
                event_dict['title'] = line.replace('SUMMARY:', '')
            elif line.startswith('DESCRIPTION:'):
                event_dict['description'] = line.replace('DESCRIPTION:', '')
            elif line.startswith('LOCATION:'):
                event_dict['location'] = line.replace('LOCATION:', '')
            elif line.startswith('UID:'):
                event_dict['uid'] = line.replace('UID:', '')
            elif line.startswith('DTSTART'):
                try:
                    date_str = line.split(':')[1]
                    # Преобразуем дату из формата YYYYMMDDTHHMMSS
                    dt = datetime.datetime.strptime(date_str[:15], '%Y%m%dT%H%M%S')
                    event_dict['start_time'] = dt.isoformat()
                    event_dict['start_display'] = dt.strftime('%d.%m.%Y %H:%M')
                except Exception:
                    # Если формат даты другой, пропускаем
                    pass
            elif line.startswith('DTEND'):
                try:
                    date_str = line.split(':')[1]
                    dt = datetime.datetime.strptime(date_str[:15], '%Y%m%dT%H%M%S')
                    event_dict['end_time'] = dt.isoformat()
                    event_dict['end_display'] = dt.strftime('%d.%m.%Y %H:%M')
                except Exception:
                    # Если формат даты другой, пропускаем
                    pass
            elif line.startswith('CREATED'):
                try:
                    date_str = line.split(':')[1]
                    dt = datetime.datetime.strptime(date_str[:15], '%Y%m%dT%H%M%S')
                    event_dict['created'] = dt.isoformat()
                except Exception:
                    # Если формат даты другой, пропускаем
                    pass
            elif line.startswith('LAST-MODIFIED'):
                try:
                    date_str = line.split(':')[1]
                    dt = datetime.datetime.strptime(date_str[:15], '%Y%m%dT%H%M%S')
                    event_dict['last_modified'] = dt.isoformat()
                except Exception:
                    # Если формат даты другой, пропускаем
                    pass
            elif line.startswith('CATEGORIES:'):
                event_dict['categories'] = line.replace('CATEGORIES:', '').split(',')
            elif line.startswith('STATUS:'):
                event_dict['status'] = line.replace('STATUS:', '')
            elif line.startswith('TRANSP:'):
                event_dict['transparency'] = line.replace('TRANSP:', '')
            elif line.startswith('SEQUENCE:'):
                try:
                    event_dict['sequence'] = int(line.replace('SEQUENCE:', ''))
                except ValueError:
                    pass
                
        return event_dict

    async def create_event(self, title: str, start: datetime.datetime, 
                           end: datetime.datetime, description: str = "") -> str:
        """
        Создать новое событие через CalDAV
        
        Args:
            title (str): Название события
            start (datetime.datetime): Дата и время начала события
            end (datetime.datetime): Дата и время окончания события
            description (str, optional): Описание события. По умолчанию: ""
            
        Returns:
            str: Сообщение о результате создания события
        """
        if not self.caldav_calendar:
            return "CalDAV не настроен"
            
        event_uid = f"{datetime.datetime.now().timestamp()}@yandex.ru"
        ical = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{title}
DESCRIPTION:{description}
UID:{event_uid}
END:VEVENT
END:VCALENDAR"""

        # Используем блок asyncio для выполнения синхронной операции в асинхронном контексте
        import asyncio
        try:
            # Выполняем синхронную операцию в отдельном потоке
            # чтобы не блокировать основной поток выполнения
            def _add_event():
                return self.caldav_calendar.add_event(ical)
                
            await asyncio.to_thread(_add_event)
            return f"Событие '{title}' успешно создано"
        except Exception as e:
            return f"Ошибка создания события: {str(e)}"

    async def delete_event(self, event_uid: str) -> str:
        """
        Удалить событие по UID
        
        Args:
            event_uid (str): Уникальный идентификатор события для удаления
            
        Returns:
            str: Сообщение о результате удаления события
        """
        if not self.caldav_calendar:
            return "CalDAV не настроен"
        
        import asyncio  
        try:
            # Выполняем синхронные операции CalDAV в отдельном потоке
            def _delete_event():
                event = self.caldav_calendar.object_by_uid(event_uid)
                if event:
                    event.delete()
                    return f"Событие {event_uid} успешно удалено"
                return "Событие не найдено"
                
            result = await asyncio.to_thread(_delete_event)
            return result
        except Exception as e:
            return f"Ошибка удаления: {str(e)}"

    async def get_upcoming_events(self, days: int = 90, format_type: str = "json") -> Union[str, Dict[str, Any]]:
        """
        Получить предстоящие события из календаря
        
        Args:
            days (int): Количество дней для просмотра предстоящих событий. По умолчанию: 90.
            format_type (str): Формат вывода: "text" или "json". По умолчанию: "json".
            
        Returns:
            Union[str, Dict[str, Any]]: Форматированный текст или JSON со списком событий, или сообщение об ошибке
        """
        if not self.caldav_calendar:
            return "CalDAV не настроен"
        
        import asyncio    
        try:
            # Вычисляем даты начала и конца периода
            start = datetime.datetime.now()
            end = start + datetime.timedelta(days=days)
            
            # Выполняем синхронные операции в отдельном потоке
            def _get_events():
                # Получаем события за указанный период
                events = self.caldav_calendar.date_search(
                    start=start,
                    end=end
                )
                
                if not events:
                    return []
                
                # Список для хранения данных событий
                events_data = []
                
                for event in events:
                    try:
                        # Получить полные данные события
                        event_data = self._parse_ical_event(event.data)
                        
                        # Получаем URL события (для обновления/удаления) - преобразуем в строку
                        event_data["url"] = str(event.url)
                        
                        events_data.append(event_data)
                    except Exception as e:
                        print(f"Ошибка при обработке события: {str(e)}")
                        continue
                
                return events_data
            
            # Выполняем в отдельном потоке, чтобы не блокировать асинхронный контекст
            events_data = await asyncio.to_thread(_get_events)
            
            if not events_data:
                if format_type.lower() == "json":
                    return {"events": [], "count": 0}
                return "Нет предстоящих событий"
            
            # Сортируем события по дате начала
            events_data.sort(key=lambda x: x.get('start_time', ''))
            
            if format_type.lower() == "json":
                return {
                    "events": events_data,
                    "count": len(events_data)
                }
            else:
                # Формируем текстовый вывод
                result = []
                for event in events_data:
                    event_str = f"📅 {event.get('title', 'Без названия')}\n"
                    event_str += f"   ID: {event.get('uid', 'Нет ID')}\n"
                    event_str += f"   Начало: {event.get('start_display', 'Не указано')}\n"
                    
                    if 'end_display' in event:
                        event_str += f"   Окончание: {event['end_display']}\n"
                    
                    if 'description' in event and event['description']:
                        event_str += f"   Описание: {event['description']}\n"
                    
                    if 'location' in event and event['location']:
                        event_str += f"   Место: {event['location']}\n"
                    
                    result.append(event_str)
                
                return "\n".join(result) if result else "Нет предстоящих событий"
            
        except Exception as e:
            error_msg = f"Ошибка при получении событий: {str(e)}"
            if format_type.lower() == "json":
                return {"error": error_msg}
            return error_msg
