from datetime import datetime
import random

from yacut import db
from yacut.constants import (
    MAX_ORIGINAL_LENGTH,
    MAX_SHORT_LENGTH,
    GENERATED_SHORT_LENGTH,
    MAX_GENERATION_ATTEMPTS,
    SHORT_PATTERN,
    SHORT_CHARS,
    SHORT_EXISTS_MESSAGE,
    INVALID_SHORT_MESSAGE,
    FILES_ENDPOINT,
    GENERATION_LIMIT_MESSAGE,
    DATABASE_ERROR_MESSAGE
)


class URLMap(db.Model):
    __tablename__ = 'url_maps'

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

    def get_short_url(self, base_url):
        """Метод для получения полного короткого URL."""
        return f'{base_url.rstrip("/")}/{self.short}'

    @classmethod
    def get_unique_short(cls):
        """Метод для генерации уникального короткого идентификатора."""
        for _ in range(MAX_GENERATION_ATTEMPTS):
            short = ''.join(
                random.choices(SHORT_CHARS, k=GENERATED_SHORT_LENGTH)
            )
            if not cls.is_short_exists(short):
                return short

        raise RuntimeError(GENERATION_LIMIT_MESSAGE)

    @classmethod
    def get_short(cls, short):
        """Метод для получения записи по короткому идентификатору."""
        return cls.query.filter_by(short=short).first()

    @classmethod
    def is_short_exists(cls, short):
        """Метод для проверки существования короткого идентификатора."""
        return cls.get_short(short) is not None

    @classmethod
    def validate(cls, short, is_custom=True):
        """Метод для валидации короткого идентификатора."""
        if not short:
            return True, None

        if short == FILES_ENDPOINT:
            return False, SHORT_EXISTS_MESSAGE

        if len(short) > MAX_SHORT_LENGTH:
            return False, INVALID_SHORT_MESSAGE

        if not SHORT_PATTERN.match(short):
            return False, INVALID_SHORT_MESSAGE

        if is_custom and cls.is_short_exists(short):
            return False, SHORT_EXISTS_MESSAGE

        return True, None

    @classmethod
    def create(
        cls,
        original_url,
        short,
        validate=True,
        skip_existing_check=False
    ):
        """Метод для создания новой записи URLMap."""
        if validate:
            is_custom = not skip_existing_check
            is_valid, error_message = cls.validate(short, is_custom)
            if not is_valid:
                return None, error_message

        if not skip_existing_check and cls.is_short_exists(short):
            return None, SHORT_EXISTS_MESSAGE

        url_map = cls(original=original_url, short=short)
        db.session.add(url_map)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return None, DATABASE_ERROR_MESSAGE

        return url_map, None

    def to_dict(self, base_url=''):
        """Метод для сериализации объекта в словарь для API."""
        result = {
            'url': self.original,
            'short_link': (
                self.get_short_url(base_url) if base_url else self.short
            )
        }

        return result
