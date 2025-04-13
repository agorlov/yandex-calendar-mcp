import asyncio
import datetime
from yandex_calendar_events2 import YandexCalendarEvents
import caldav
# Замените эти значения на ваши данные
# Пароль генерируется в личном кабинете Яндекса
# https://id.yandex.ru/security/app-passwords
# CALDAV_URL = "https://caldav.yandex.ru/calendars/alexgorlov%40yandex.ru/events-18184974/"
CALDAV_URL = "https://caldav.yandex.ru/"
USERNAME = "alexgorlov@yandex.ru" # ag_calendar"
PASSWORD = "cjrtixyphmhwzdxe"

client = caldav.DAVClient(url='https://caldav.yandex.ru/', username=USERNAME, password=PASSWORD)
#calendar = client.principal().calendar("https://caldav.yandex.ru/calendars/alexgorlov%40yandex.ru/events-18184974/")
#calendar = client.principal().calendar(18184974)
# my_principal = client.principal()
# calendars = my_principal.calendars()


# for c in calendars:
#     print("    Name: %-36s  URL: %s" % (c.name, c.url))

# calendar = client.principal().calendar("Мои события")
# print(calendar)


async def main():
    print("Инициализация календаря...")
    calendar = YandexCalendarEvents(CALDAV_URL, USERNAME, PASSWORD)

    # Создание события
    # title = "Тестовое событие"
    # start = datetime.datetime.now() + datetime.timedelta(days=1)  # Завтра
    # end = start + datetime.timedelta(hours=1)  # На час позже
    # description = "Описание тестового события"

    # print(f"Создание события: {title} с {start} по {end}...")
    # create_response = await calendar.create_event(title, start, end, description)
    # print(create_response)

    # Получение списка событий
    # print("Получение списка событий...")

    # events = calendar.caldav_calendar.events()
    # print("Список событий:")
    # for event in events:
    #     # print(event.data)
    #     print(f"- {event.icalendar_component["summary"]} (UID: {event.icalendar_component["uid"]})")
    calendar.delete_event("1744475299.610976@yandex.ru")


if __name__ == "__main__":
    asyncio.run(main())