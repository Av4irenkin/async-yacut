from flask import abort, flash, render_template, redirect, url_for

from yacut import app
from yacut.disk_client import disk_uploader
from yacut.models import URLMap
from yacut.forms import URLForm, FileUploadForm


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница."""
    form = URLForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    original_url = form.original_link.data
    custom_id = (
        form.custom_id.data.strip() if form.custom_id.data else None
    )

    if custom_id:
        url_map, error_message = URLMap.create(
            original_url=original_url,
            short=custom_id,
            validate=True,
            skip_existing_check=False
        )
    else:
        url_map, error_message = URLMap.create(
            original_url=original_url,
            short=URLMap.get_unique_short(),
            validate=False,
            skip_existing_check=True
        )

    if error_message:
        flash(error_message, 'danger')
        return render_template('index.html', form=form)

    return render_template(
        'index.html',
        form=form,
        short_url=url_for(
            'redirect_view',
            short=url_map.short,
            _external=True
        ),
        original_url=original_url
    )


@app.route('/<short>')
def redirect_view(short):
    """Перенаправление по короткой ссылке."""
    url_map = URLMap.get_short(short)
    if not url_map:
        abort(404)
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    """Страница загрузки файлов на Яндекс диск."""
    form = FileUploadForm()

    if not form.validate_on_submit():
        return render_template('files.html', form=form)

    files = form.files.data

    try:
        uploaded_files = [
            {
                'name': result['name'],
                'short_url': url_for(
                    'redirect_view',
                    short=url_map.short,
                    _external=True
                )
            }
            for result in disk_uploader.upload_files_sync(files)
            for url_map, error_message in [URLMap.create(
                original_url=result['download_url'],
                short=URLMap.get_unique_short(),
                validate=False,
                skip_existing_check=True
            )]
            if not error_message
        ]

    except Exception as e:
        app.logger.error(f'Ошибка загрузки файлов: {e}')
        uploaded_files = []

    return render_template(
        'files.html',
        form=form,
        uploaded_files=uploaded_files
    )
