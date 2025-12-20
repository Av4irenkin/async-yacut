import random
import string

from yacut.models import URLMap


def get_unique_short_id(length=6):
    """
    Метод для генерации коротких ссылок
    и проверки их наличия в базе данных.
    """

    while True:
        short_id = ''.join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
