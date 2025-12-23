from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus

from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import models
from .api_views import api_blueprint
from .error_handlers import page_not_found, internal_server_error

app.register_blueprint(api_blueprint)
app.register_error_handler(HTTPStatus.NOT_FOUND, page_not_found)
app.register_error_handler(
    HTTPStatus.INTERNAL_SERVER_ERROR,
    internal_server_error
)

from . import views
