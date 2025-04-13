import asyncio
import datetime
from yandex_calendar_events2 import YandexCalendarEvents

async def main():
    # Используйте базовый URL без конкретного календаря
    CALDAV_BASE_URL = "https://caldav.yandex.ru"
    USERNAME = "alexgorlov@yandex.ru"
    PASSWORD = "cjrtixyphmhwzdxe"  # Пароль приложения
    
    print("Инициализация календаря...")
    calendar = YandexCalendarEvents(
        caldav_url=CALDAV_BASE_URL,
        username=USERNAME,
        password=PASSWORD
    )
    
    if not calendar.caldav_calendar:
        print("Не удалось подключиться к CalDAV")
        return

    # Тестирование создания события
    title = "Тестовое событие (удалить меня)"
    start = datetime.datetime.now() + datetime.timedelta(days=1)
    end = start + datetime.timedelta(hours=1)
    
    print(f"\n1. Создание тестового события: {title}...")
    create_result = await calendar.create_event(title, start, end)
    print(create_result)

    # Получение списка событий для поиска только что созданного
    print("\n2. Поиск созданного события...")
    try:
        events = calendar.caldav_calendar.date_search(
            start=datetime.datetime.now(),
            end=datetime.datetime.now() + datetime.timedelta(days=2))
        
        test_event = None
        for event in events:
            print(f"- {event.instance.vevent.summary.value} (UID: {event.instance.vevent.uid.value})")
            if event.instance.vevent.summary.value == title:
                test_event = event
                break
        
        if test_event:
            print("\n3. Удаление тестового события...")
            uid = test_event.instance.vevent.uid.value
            delete_result = await calendar.delete_event(uid)
            print(delete_result)
            
            # Проверка что событие удалено
            print("\n4. Проверка удаления события...")
            events_after_delete = calendar.caldav_calendar.date_search(
                start=datetime.datetime.now(),
                end=datetime.datetime.now() + datetime.timedelta(days=2))
            
            found = False
            for event in events_after_delete:
                if event.instance.vevent.uid.value == uid:
                    found = True
                    break
            
            if not found:
                print("Событие успешно удалено!")
            else:
                print("Ошибка: событие не было удалено")
        else:
            print("Тестовое событие не найдено для удаления")
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())