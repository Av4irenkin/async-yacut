import re

from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import (DataRequired, URL, Length,
                                Optional, ValidationError)


def validate_short_id(form, field):
    """Валидатор для короткого идентификатора"""
    if field.data:
        if not re.match(r'^[A-Za-z0-9]+$', field.data):
            raise ValidationError(
                'Идентификатор должен содержать только буквы и цифры'
            )


class URLForm(FlaskForm):
    """Форма для укорачивания ссылок"""
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Введите корректный URL')
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'https://example.com/very/long/url'
        }
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=16, message='Не более 16 символов'),
            validate_short_id
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Необязательное поле'
        }
    )
    submit = SubmitField(
        'Создать',
        render_kw={'class': 'btn btn-primary'}
    )


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов на Яндекс.Диск"""
    files = MultipleFileField(
        'Выберите файлы',
        validators=[DataRequired(message='Выберите хотя бы один файл')],
        render_kw={'class': 'form-control-file'}
    )

    submit = SubmitField(
        'Загрузить',
        render_kw={'class': 'btn btn-primary'}
    )
