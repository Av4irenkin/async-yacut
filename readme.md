# YaCut - сервис укорачивания ссылок и загрузки файлов

YaCut — это веб-сервис для укорачивания длинных ссылок и асинхронной загрузки файлов на Яндекс.Диск с генерацией коротких ссылок для скачивания.

## Возможности

- **Укорачивание ссылок**: преобразование длинных URL в короткие (6 случайных символов или пользовательский вариант)
- **Переадресация**: автоматическое перенаправление по коротким ссылкам на оригинальные адреса
- **Валидация**: проверка корректности URL и уникальности коротких идентификаторов
- **API**: REST API для интеграции с другими сервисами
- **Загрузка файлов**: асинхронная загрузка нескольких файлов на Яндекс.Диск
- **Короткие ссылки для файлов**: автоматическая генерация коротких ссылок для загруженных файлов

## Технологии

- **Backend**: Python 3.12, Flask, SQLAlchemy, Flask-Migrate
- **Frontend**: HTML5, Bootstrap 4, JavaScript
- **База данных**: SQLite (разработка), поддержка других БД через SQLAlchemy
- **API Яндекс.Диска**: aiohttp для асинхронных запросов
- **Валидация форм**: Flask-WTF, WTForms

## Как запустить проект Yacut:

### Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/Av4irenkin/async-yacut.git
```

### Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```bash
    source venv/bin/activate
    ```

* Если у вас windows

    ```bash
    source venv/scripts/activate
    ```

### Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### Создать в директории проекта файл .env с четыремя переменными окружения:

```
FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=your_secret_key
DB=sqlite:///db.sqlite3
```

### Создать базу данных и применить миграции:

```bash
flask db upgrade
```

### Запустить проект:

```bash
flask run
```

### Сервис будет доступен по адресу: [YaCut](http://127.0.0.1:5000)

## Для получения DISK_TOKEN:
1) Создайте приложение на Яндекс OAuth
2) Укажите права: cloud_api:disk.app_folder, cloud_api:disk.info
3) Получите OAuth-токен
4) Добавьте его в .env

## API Endpoints

### Создание короткой ссылки

**Request**: POST /api/id/
```json
{
  "url": "https://example.com/very/long/url",
  "custom_id": "my-link"
}
```

**Response (201)**:
```json
{
  "url": "https://example.com/very/long/url",
  "short_link": "http://yacut.ru/my-link"
}
```

### Получение оригинальной ссылки

**Request**: GET /api/id/<short_id>/

**Response (200)**:
```json
{
  "url": "https://example.com/very/long/url"
}
```

**Response (404)**:
```json
{
  "message": "Указанный id не найден"
}
```

## Автор
Автор проекта: [Иван Овчаренко](https://github.com/Av4irenkin) [Av4rnk@gmail.com](Av4rnk@gmail.com)