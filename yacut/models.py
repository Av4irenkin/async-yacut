from datetime import datetime
import random

from flask import url_for

from yacut import db
from yacut.constants import (
    MAX_ORIGINAL_LENGTH,
    MAX_SHORT_LENGTH,
    GENERATED_SHORT_LENGTH,
    MAX_GENERATION_ATTEMPTS,
    SHORT_PATTERN,
    SHORT_CHARS,
    FILES_ENDPOINT,
)

INVALID_SHORT_MESSAGE = 'Указано недопустимое имя для короткой ссылки'
GENERATION_LIMIT_MESSAGE = (
    'Не удалось сгенерировать уникальную короткую ссылку'
    f' за {MAX_GENERATION_ATTEMPTS} попыток'
)
SHORT_EXISTS_MESSAGE = (
    'Предложенный вариант короткой ссылки уже существует.'
)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_ORIGINAL_LENGTH), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'URLMap(original={self.original}, short={self.short})'

    @staticmethod
    def get(short):
        """Метод для получения записи по короткому идентификатору."""
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def get_unique_short():
        """Метод для генерации уникального короткого идентификатора."""
        for _ in range(MAX_GENERATION_ATTEMPTS):
            short = ''.join(
                random.choices(SHORT_CHARS, k=GENERATED_SHORT_LENGTH)
            )
            if not URLMap.get(short) and short != FILES_ENDPOINT:
                return short

        raise RuntimeError(GENERATION_LIMIT_MESSAGE)

    def get_short_url(self):
        """Метод для получения полного короткого URL."""
        return url_for('redirect_view', short=self.short, _external=True)

    @staticmethod
    def create(original_url, short=None):
        """Метод для создания новой записи URLMap."""
        if not short:
            short = URLMap.get_unique_short()
        else:
            if short == FILES_ENDPOINT:
                return None, SHORT_EXISTS_MESSAGE

            if len(short) > MAX_SHORT_LENGTH:
                return None, INVALID_SHORT_MESSAGE

            if not SHORT_PATTERN.match(short):
                return None, INVALID_SHORT_MESSAGE

            if URLMap.get(short):
                return None, SHORT_EXISTS_MESSAGE

        url_map = URLMap(original=original_url, short=short)
        db.session.add(url_map)
        db.session.commit()

        return url_map
