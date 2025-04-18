"""
Пакет тестов для MCP-сервера Яндекс Календаря

Содержит следующие тесты:
- test.py: Интеграционный тест всего цикла (создание, поиск, удаление события)
- show_events.py: Просмотр событий на следующую неделю
- test_create_event.py: Тест создания одного события
- test_json_events.py: Получение событий в JSON и опция удаления

Для запуска всех тестов используйте скрипт run_tests.py в корневой директории:
  python run_tests.py

Для запуска конкретного теста:
  python run_tests.py <имя_теста>
  Например: python run_tests.py test_json_events
"""

# Этот файл помогает Python распознать директорию tests как пакет
# и упрощает импорт между тестовыми модулями
