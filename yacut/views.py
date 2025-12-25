from flask import abort, flash, render_template, redirect
from http import HTTPStatus

from yacut import app
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
        url_map = URLMap.create(
            original_url=form.original_link.data,
            short=form.custom_id.data
        )
    except Exception:
        flash(SHORT_CREATION_ERROR, 'danger')
        return render_template('index.html', form=form)

    return render_template(
        'index.html',
        form=form,
        short_url=url_map.get_short_url()
    )


@app.route('/<short>')
def redirect_view(short):
    """Перенаправление по короткой ссылке."""
    url_map = URLMap.get(short)
    if not url_map:
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
        flash(UPLOAD_ERROR, 'danger')
        return render_template('files.html', form=form)

    uploaded_files = [
        {'name': file.filename, 'short_url': url_map.get_short_url()}
        for file, download_url in zip(files, download_urls)
        for url_map in [
            URLMap.create(original_url=download_url)
        ]
        if url_map is not None
    ]

    return render_template(
        'files.html',
        form=form,
        uploaded_files=uploaded_files
    )
