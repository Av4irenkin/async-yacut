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
CUSTOM_SHORT_LABEL = 'Ваш вариант короткой ссылки'
CUSTOM_SHORT_PLACEHOLDER = 'Необязательное поле'
CREATE_BUTTON = 'Создать'
CHOOSE_FILES_LABEL = 'Выберите файлы'
UPLOAD_BUTTON = 'Загрузить'

REQUIRED_FIELD_MESSAGE = 'Обязательное поле'
INVALID_URL_MESSAGE_FORM = 'Введите корректный URL'
MAX_LENGTH_MESSAGE = 'Не более {max} символов'
INVALID_CHARS_MESSAGE = 'Идентификатор должен содержать только буквы и цифры'
CHOOSE_FILE_MESSAGE = 'Выберите хотя бы один файл'
SHORT_EXISTS_MESSAGE_FORM = (
    'Предложенный вариант короткой ссылки уже существует.'
)


class URLForm(FlaskForm):
    """Форма для укорачивания ссылок"""

    def validate_custom_short(self, field):
        """Валидатор для короткого идентификатора (метод формы)"""
        if not field.data:
            return
        if field.data == FILES_ENDPOINT or URLMap.is_short_exists(field.data):
            raise ValidationError(SHORT_EXISTS_MESSAGE_FORM)

    original_link = URLField(
        LONG_LINK_LABEL,
        validators=[
            DataRequired(message=REQUIRED_FIELD_MESSAGE),
            URL(message=INVALID_URL_MESSAGE_FORM),
            Length(
                max=MAX_ORIGINAL_LENGTH,
                message=MAX_LENGTH_MESSAGE.format(max=MAX_ORIGINAL_LENGTH)
            )
        ],
    )
    custom_id = StringField(
        CUSTOM_SHORT_LABEL,
        validators=[
            Optional(),
            Length(max=MAX_SHORT_LENGTH,
                   message=MAX_LENGTH_MESSAGE.format(max=MAX_SHORT_LENGTH)),
            Regexp(
                SHORT_PATTERN,
                message=INVALID_CHARS_MESSAGE
            ),
            validate_custom_short
        ],
    )
    submit = SubmitField(
        CREATE_BUTTON,
    )


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс.Диск"""
    files = MultipleFileField(
        CHOOSE_FILES_LABEL,
        validators=[DataRequired(message=CHOOSE_FILE_MESSAGE)],
    )

    submit = SubmitField(
        UPLOAD_BUTTON,
    )
