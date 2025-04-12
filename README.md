# Сервер MCP для Яндекс Календаря

Простой MCP сервер для доступа к событиям из Яндекс Календаря.
(Мой Hello-World-MCP)

## О создании MCP

- Офиц гайд https://modelcontextprotocol.io/introduction
- Сэмплы mcp-серверов https://github.com/punkpeye/awesome-mcp-servers/
- Ещё сэмплы https://github.com/modelcontextprotocol/servers
- Примеры https://modelcontextprotocol.io/examples (там всякие gdrive, git, базы данных и тд)
- Хорошая статья про создание агентов: https://www.anthropic.com/engineering/building-effective-agents

## Установка

```bash
pip install "mcp[cli]" httpx beautifulsoup4
```

## Получение URL Яндекс Календаря

1. Войдите в Яндекс Календарь
2. Слева, рядом с нужным календарем нажать на шестеренку (настройки)
3. Найдите раздел "Экспорт" или "Внешний доступ"
4. Скопируйте HTML-ссылку для экспорта, которая выглядит примерно так:
   ```
   https://calendar.yandex.ru/export/html.xml?private_token=XXXXX&tz_id=Europe/Moscow&limit=90
   ```



## Запуск сервера

```bash
path/venv/bin/python main.py "https://calendar.yandex.ru/export/html.xml?private_token=XXXXX&tz_id=Europe/Moscow&limit=90"
```

## Настройка для Claude Desktop

Файл конфигурации:
- MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": [
        "@wonderwhy-er/desktop-commander"
      ]
    },
    "yandex-calendar": {
      "command": "/home/[path]/projects/ya-cal-mcp/venv/bin/python",
      "args": [
        "/home/[path]/projects/ya-cal-mcp/main.py",
        "https://calendar.yandex.ru/export/html.xml?private_token=XXXXX&tz_id=Europe/Moscow&limit=90"
      ]
    }
  }
}

```

## Использование

Доступный инструмент:
- `get_upcoming_events`: Получить предстоящие события на указанное количество дней (по умолчанию 90)

Просто спросите Чат о ваших предстоящих событиях, и он воспользуется этим инструментом.
