from flask import render_template, redirect, flash, request, abort

from yacut import app, db
from yacut.disk_client import disk_uploader
from yacut.models import URLMap
from yacut.forms import URLForm, FileUploadForm
from yacut.utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница."""
    form = URLForm()
    if form.validate_on_submit():
        original_url = form.original_link.data
        custom_id = (
            form.custom_id.data.strip() if form.custom_id.data else None
        )
        if custom_id:
            if custom_id == 'files':
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'danger'
                )
                return render_template('index.html', form=form)
            if URLMap.query.filter_by(short=custom_id).first():
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'danger'
                )
                return render_template('index.html', form=form)
        short_id = custom_id if custom_id else get_unique_short_id()
        while URLMap.query.filter_by(short=short_id).first():
            short_id = get_unique_short_id()
        db.session.add(URLMap(original=original_url, short=short_id))
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Ошибка при сохранении в базу данных.', 'danger')
            return render_template('index.html', form=form)
        return render_template('index.html',
                               form=form,
                               short_url=request.host_url + short_id,
                               original_url=original_url)
    return render_template('index.html', form=form)


@app.route('/<short_id>')
def redirect_view(short_id):
    """Перенаправление по короткой ссылке."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        abort(404)
    return redirect(url_map.original)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    """Страница загрузки файлов на Яндекс диск."""
    form = FileUploadForm()
    uploaded_files = []
    if form.validate_on_submit():
        files = request.files.getlist('files')
        if not files or all(not file.filename for file in files):
            flash('Не выбраны файлы для загрузки', 'warning')
        else:
            try:
                successful_uploads = []
                for result in disk_uploader.upload_files_sync(files):
                    if result['status'] == 'success':
                        short_id = get_unique_short_id()
                        while URLMap.query.filter_by(short=short_id).first():
                            short_id = get_unique_short_id()
                        db.session.add(
                            URLMap(
                                original=result['download_url'],
                                short=short_id
                            )
                        )
                        successful_uploads.append({
                            'name': result['name'],
                            'short_url': request.host_url + short_id,
                            'download_url': result['download_url'],
                            'size': result['size'],
                            'status': 'success'
                        })
                    else:
                        uploaded_files.append({
                            'name': result['name'],
                            'error': result.get(
                                'error',
                                'Неизвестная ошибка'
                            ),
                            'status': 'error'
                        })
                if successful_uploads:
                    db.session.commit()
                    uploaded_files.extend(successful_uploads)
                    flash(
                        f'Успешно загружено {len(successful_uploads)}'
                        ' файл(ов)',
                        'success'
                    )
                error_count = len(
                    [f for f in uploaded_files if f['status'] == 'error']
                )
                if error_count > 0:
                    flash(
                        f'Не удалось загрузить {error_count} файл(ов)',
                        'warning'
                    )
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Ошибка загрузки файлов: {e}')
                flash(f'Ошибка при загрузке файлов: {str(e)}', 'danger')
    return render_template(
        'files.html',
        form=form,
        uploaded_files=uploaded_files
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
