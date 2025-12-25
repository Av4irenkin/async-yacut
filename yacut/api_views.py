from flask import Blueprint, jsonify, request
from http import HTTPStatus

from yacut.error_handlers import APIError
from yacut.models import URLMap


LINK_REQUIRED_MESSAGE = '"url" является обязательным полем!'
MISSING_REQUEST_BODY = 'Отсутствует тело запроса'
SHORT_NOT_FOUND_MESSAGE = 'Указанный id не найден'


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api/id/', methods=['POST'])
def create_short_link():
    """Метод для создания короткой ссылки через API."""
    data = request.get_json(silent=True)

    if data is None:
        raise APIError(MISSING_REQUEST_BODY, HTTPStatus.BAD_REQUEST)

    url = data.get('url')
    if not url:
        raise APIError(LINK_REQUIRED_MESSAGE, HTTPStatus.BAD_REQUEST)

    short = data.get('custom_id')

    try:
        result = URLMap.create(original_url=url, short=short)

        if isinstance(result, tuple) and result[0] is None:
            raise APIError(result[1], HTTPStatus.BAD_REQUEST)

        url_map = result

        return jsonify({
            'url': url_map.original,
            'short_link': url_map.get_short_url()
        }), HTTPStatus.CREATED

    except RuntimeError as e:
        raise APIError(str(e), HTTPStatus.BAD_REQUEST)


@api_blueprint.route('/api/id/<short>/', methods=['GET'])
def get_original_link(short):
    """Метод получения оригинальной ссылки по короткому идентификатору."""
    url_map = URLMap.get(short)
    if not url_map:
        raise APIError(SHORT_NOT_FOUND_MESSAGE, HTTPStatus.NOT_FOUND)

    return jsonify({'url': url_map.original})
