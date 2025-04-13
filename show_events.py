import asyncio
import datetime
from yandex_calendar_events2 import YandexCalendarEvents

async def main():
    CALDAV_BASE_URL = "https://caldav.yandex.ru"
    USERNAME = "alexgorlov@yandex.ru"
    PASSWORD = "cjrtixyphmhwzdxe"
    
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