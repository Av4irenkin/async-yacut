import os

from dotenv import load_dotenv


load_dotenv()


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'sqlite:///db.sqlite3'
    )
    SECRET_KEY = os.getenv('SECRET_KEY', 'my-secret-key')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    YANDEX_DISK_BASE_URL = os.getenv(
        'YANDEX_DISK_BASE_URL',
        'https://cloud-api.yandex.net/v1/disk'
    )
    YANDEX_DISK_FOLDER = os.getenv(
        'YANDEX_DISK_FOLDER',
        'yacut_uploads'
    )
