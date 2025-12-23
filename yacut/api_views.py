from flask import Blueprint, jsonify, request, url_for
from http import HTTPStatus

from yacut.models import URLMap
from yacut.constants import (
    LINK_REQUIRED_MESSAGE,
    SHORT_NOT_FOUND_MESSAGE,
    MISSING_REQUEST_BODY
)


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api/id/', methods=['POST'])
def create_short_link():
    """Метод для создания короткой ссылки через API."""
    data = request.get_json(silent=True)

    if data is None:
        return jsonify(
            {'message': MISSING_REQUEST_BODY}
        ), HTTPStatus.BAD_REQUEST

    url = data.get('url')
    if not url:
        return jsonify(
            {'message': LINK_REQUIRED_MESSAGE}
        ), HTTPStatus.BAD_REQUEST

    custom_short = data.get('custom_id')

    try:
        if custom_short:
            url_map, error_message = URLMap.create(
                original_url=url,
                short=custom_short,
                validate=True,
                skip_existing_check=False
            )
        else:
            url_map, error_message = URLMap.create(
                original_url=url,
                short=URLMap.get_unique_short(),
                validate=False,
                skip_existing_check=True
            )

        if error_message:
            return jsonify(
                {'message': error_message}
            ), HTTPStatus.BAD_REQUEST

        short_link = url_for(
            'redirect_view',
            short=url_map.short,
            _external=True
        )

        return jsonify({
            'url': url_map.original,
            'short_link': short_link
        }), HTTPStatus.CREATED

    except RuntimeError as e:
        return jsonify({'message': str(e)}), HTTPStatus.BAD_REQUEST


@api_blueprint.route('/api/id/<short>/', methods=['GET'])
def get_original_link(short):
    """Метод получения оригинальной ссылки по короткому идентификатору."""
    url_map = URLMap.get_short(short)
    if not url_map:
        return jsonify(
            {'message': SHORT_NOT_FOUND_MESSAGE}
        ), HTTPStatus.NOT_FOUND

    return jsonify({'url': url_map.original})
