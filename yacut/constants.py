import re
import string


MAX_ORIGINAL_LENGTH = 2048
MAX_SHORT_LENGTH = 16
GENERATED_SHORT_LENGTH = 6
MAX_GENERATION_ATTEMPTS = 10
SHORT_CHARS = string.ascii_letters + string.digits
SHORT_PATTERN = re.compile(f'^[{re.escape(SHORT_CHARS)}]+$')
LINK_REQUIRED_MESSAGE = '"url" является обязательным полем!'
INVALID_SHORT_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
SHORT_EXISTS_MESSAGE = (
    'Предложенный вариант короткой ссылки уже существует.'
)
SHORT_NOT_FOUND_MESSAGE = 'Указанный id не найден'
GENERATION_LIMIT_MESSAGE = (
    'Не удалось сгенерировать уникальную короткую ссылку'
)
MISSING_REQUEST_BODY = 'Отсутствует тело запроса'
DATABASE_ERROR_MESSAGE = 'Ошибка базы данных'
INTERNAL_SERVER_ERROR = 'Внутренняя ошибка сервера'
ORIGINAL_LINK_FIELD = 'original_link'
CUSTOM_ID_FIELD = 'custom_id'
URL_FIELD = 'url'
SHORT_ID_FIELD = 'short_id'
FILES_ENDPOINT = 'files'
YANDEX_DISK_BASE_URL = 'https://cloud-api.yandex.net/v1/disk'
NOT_FOUND_MESSAGE = 'Страница не найдена'
INTERNAL_SERVER_ERROR_MESSAGE = 'Внутренняя ошибка сервера'
