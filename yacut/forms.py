from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.fields import URLField
from wtforms.validators import (DataRequired, URL, Length,
                                Optional, ValidationError, Regexp)

from yacut.constants import (
    MAX_ORIGINAL_LENGTH,
    MAX_SHORT_LENGTH,
    SHORT_PATTERN,
    FILES_ENDPOINT
)
from yacut.models import URLMap


LONG_LINK_LABEL = 'Длинная ссылка'
LONG_LINK_PLACEHOLDER = 'https://example.com/very/long/url'
SHORT_LABEL = 'Ваш вариант короткой ссылки'
SHORT_PLACEHOLDER = 'Необязательное поле'
CREATE_BUTTON = 'Создать'
CHOOSE_FILES_LABEL = 'Выберите файлы'
UPLOAD_BUTTON = 'Загрузить'
REQUIRED_FIELD = 'Обязательное поле'
INVALID_URL_FORM = 'Введите корректный URL'
MAX_LENGTH = f'Не более {MAX_SHORT_LENGTH} символов'
INVALID_CHARS = 'Идентификатор должен содержать только буквы и цифры'
CHOOSE_FILE = 'Выберите хотя бы один файл'
SHORT_EXISTS_FORM = (
    'Предложенный вариант короткой ссылки уже существует.'
)


class URLForm(FlaskForm):
    """Форма для укорачивания ссылок"""

    def validate_custom_id(self, field):
        """Валидатор для короткого идентификатора (метод формы)"""
        if not field.data:
            return
        if field.data == FILES_ENDPOINT or URLMap.get(field.data):
            raise ValidationError(SHORT_EXISTS_FORM)

    original_link = URLField(
        LONG_LINK_LABEL,
        validators=[
            DataRequired(message=REQUIRED_FIELD),
            URL(message=INVALID_URL_FORM),
            Length(max=MAX_ORIGINAL_LENGTH,
                   message=MAX_LENGTH)
        ],
    )
    custom_id = StringField(
        SHORT_LABEL,
        validators=[
            Optional(),
            Length(max=MAX_SHORT_LENGTH,
                   message=MAX_LENGTH),
            Regexp(SHORT_PATTERN,
                   message=INVALID_CHARS),
        ],
    )
    submit = SubmitField(
        CREATE_BUTTON,
    )


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс.Диск"""
    files = MultipleFileField(
        CHOOSE_FILES_LABEL,
        validators=[DataRequired(message=CHOOSE_FILE)],
    )
    submit = SubmitField(
        UPLOAD_BUTTON,
    )
