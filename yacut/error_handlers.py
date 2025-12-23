from http import HTTPStatus
from flask import render_template

from yacut import db


def page_not_found(e):
    """Обработчик ошибки 404."""
    return render_template('404.html'), HTTPStatus.NOT_FOUND


def internal_server_error(e):
    """Обработчик ошибки 500."""
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
