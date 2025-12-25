from flask import abort, flash, render_template, redirect

from http import HTTPStatus

from yacut import app
from yacut.constants import REDIRECT_VIEW_NAME
from yacut.disk_client import disk_uploader
from yacut.models import URLMap
from yacut.forms import URLForm, FileUploadForm


SHORT_CREATION_ERROR = 'Ошибка при создании короткой ссылки'
UPLOAD_ERROR = 'Ошибка при загрузке файлов на Яндекс.Диск'


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница."""
    form = URLForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        return render_template(
            'index.html',
            form=form,
            short_url=URLMap.create(
                original_url=form.original_link.data,
                short=form.custom_id.data,
                validate=False
            ).get_short_url()
        )
    except (RuntimeError, ValueError):
        flash(SHORT_CREATION_ERROR)
        return render_template('index.html', form=form)


@app.route('/<short>', endpoint=REDIRECT_VIEW_NAME)
def redirect_view(short):
    """Перенаправление по короткой ссылке."""
    if (url_map := URLMap.get(short)) is None:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    """Страница загрузки файлов на Яндекс диск."""
    form = FileUploadForm()

    if not form.validate_on_submit():
        return render_template('files.html', form=form)

    files = form.files.data

    try:
        download_urls = disk_uploader.upload_files_sync(files)
    except Exception:
        flash(UPLOAD_ERROR)
        return render_template('files.html', form=form)

    def process_file(file, download_url):
        try:
            return [{
                'name': file.filename,
                'short_url': URLMap.create(
                    original_url=download_url,
                    short=None,
                    validate=True
                ).get_short_url()
            }]
        except (RuntimeError, ValueError):
            return []

    return render_template(
        'files.html',
        form=form,
        uploaded_files=[
            result
            for file, download_url in zip(files, download_urls)
            for result in process_file(file, download_url)
        ]
    )
