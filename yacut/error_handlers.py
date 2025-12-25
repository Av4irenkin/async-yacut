from flask import jsonify, render_template
from http import HTTPStatus

from yacut import db


class APIError(Exception):
    """Базовый класс исключений для API контроллеров."""

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code


def api_error_handler(error):
    """Обработчик ошибок API."""
    response = jsonify({'message': error.message})
    response.status_code = error.status_code
    return response


def page_not_found(e):
    """Обработчик ошибки 404."""
    return render_template('404.html'), HTTPStatus.NOT_FOUND


def internal_server_error(e):
    """Обработчик ошибки 500."""
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
