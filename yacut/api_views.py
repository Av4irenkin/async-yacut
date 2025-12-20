import re

from flask import Blueprint, jsonify, request
from urllib.parse import urlparse

from yacut import db
from yacut.models import URLMap
from yacut.utils import get_unique_short_id


api_blueprint = Blueprint('api', __name__)


def validate_url(url):
    """Валидация URL"""
    try:
        result = urlparse(url)
        return bool(result.scheme) and bool(result.netloc)
    except Exception:
        return False


def _validate_request_data(data):
    """Валидация данных запроса."""
    if data is None:
        return False, {'message': 'Отсутствует тело запроса'}, 400
    url = data.get('url')
    if not url:
        return False, {'message': '"url" является обязательным полем!'}, 400
    url = url.strip()
    if not validate_url(url):
        return False, {'message': 'Некорректный URL'}, 400
    return True, {'url': url}, 200


def _validate_custom_id(custom_id):
    """Валидация варианта короткой ссылки."""
    if not custom_id:
        return True, None
    if len(custom_id) > 16 or not re.match(r'^[A-Za-z0-9]+$', custom_id):
        return False, 'Указано недопустимое имя для короткой ссылки'
    if URLMap.query.filter_by(short=custom_id).first():
        return False, 'Предложенный вариант короткой ссылки уже существует.'
    return True, None


def _generate_short_id(custom_id):
    """Генерация уникального короткого идентификатора."""
    if custom_id:
        return custom_id
    short_id = get_unique_short_id()
    while URLMap.query.filter_by(short=short_id).first():
        short_id = get_unique_short_id()
    return short_id


@api_blueprint.route('/api/id/', methods=['POST'])
def create_short_link():
    """Создание короткой ссылки через API."""
    data = request.get_json(silent=True)
    is_valid, response_data, status_code = _validate_request_data(data)
    if not is_valid:
        return jsonify(response_data), status_code
    url = response_data['url']
    custom_id = data.get('custom_id')
    is_valid, error_message = _validate_custom_id(custom_id)
    if not is_valid:
        return jsonify({'message': error_message}), 400
    short_id = _generate_short_id(custom_id)
    try:
        url_map = URLMap(original=url, short=short_id)
        db.session.add(url_map)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'Ошибка базы данных'}), 500
    return jsonify({
        'url': url,
        'short_link': request.host_url + short_id
    }), 201


@api_blueprint.route('/api/id/<short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получение оригинальной ссылки по короткому идентификатору"""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify({'message': 'Указанный id не найден'}), 404
    return jsonify({'url': url_map.original}), 200
