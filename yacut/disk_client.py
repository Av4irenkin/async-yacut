import aiohttp
import asyncio
import re
import os

from yacut import app


class YaDiskUploader:
    """Класс для асинхронной загрузки файлов на Яндекс диск."""

    def __init__(self):
        self.token = os.getenv('DISK_TOKEN')
        self.base_url = 'https://cloud-api.yandex.net/v1/disk'
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json'
        }
        if not self.token:
            app.logger.warning(
                'DISK_TOKEN не установлен.'
            )

    async def _make_request(self, method, endpoint, **kwargs):
        """Метод для выполнения HTTP-запросов."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.request(
                method,
                f'{self.base_url}/{endpoint}',
                **kwargs
            ) as response:
                if response.status >= 400:
                    app.logger.error(
                        f'API Error {response.status}:'
                        f' {await response.text()}'
                    )
                response.raise_for_status()
                if response.status != 204:
                    return await response.json()
                return None

    async def create_folder(self, folder_path):
        """Метод создания папки на Яндекс диске."""
        try:
            await self._make_request('PUT', f'resources?path={folder_path}')
            app.logger.info(f'Создана папка: {folder_path}')
            return True
        except aiohttp.ClientResponseError as e:
            if e.status == 409:
                app.logger.info(f'Папка {folder_path} уже существует')
                return True
            else:
                app.logger.error(f'Ошибка создания папки {folder_path}: {e}')
                raise

    async def get_upload_link(self, file_path):
        """Метод получения ссылки для загрузки файла."""
        response = await self._make_request(
            'GET',
            'resources/upload',
            params={'path': file_path, 'overwrite': 'true'}
        )
        return response['href']

    async def upload_file(self, upload_url, file_content):
        """Метод загрузки файла на Яндекс диск."""
        async with aiohttp.ClientSession() as session:
            async with session.put(upload_url, data=file_content) as response:
                response.raise_for_status()
                return True

    async def get_download_link(self, file_path):
        """Метод для получения ссылки для скачивания файла."""
        response = await self._make_request(
            'GET',
            'resources/download',
            params={'path': file_path}
        )
        return response['href']

    def _make_filename_safe(self, filename):
        """Делает имя файла безопасным для Яндекс диска."""
        name, ext = os.path.splitext(filename)
        return re.sub(r'[^\w\-\.]', '_', name)[:100] + ext

    async def upload_files(self, files):
        """Асинхронная загрузка файлов."""
        results = []
        folder_name = (
            'app:/yacut_uploads'
        )
        try:
            app.logger.info(f'Начата загрузка в папку {folder_name}')
            for file in files:
                try:
                    original_filename = file.filename
                    file_content = file.read()
                    if not file_content:
                        raise ValueError('Файл пустой')
                    file_path = (
                        f'{folder_name}/'
                        f'{self._make_filename_safe(original_filename)}'
                    )
                    app.logger.info(f'Получена ссылка для {original_filename}')
                    await self.upload_file(
                        await self.get_upload_link(file_path),
                        file_content
                    )
                    app.logger.info(f'Файл {original_filename} загружен')
                    download_link = await self.get_download_link(file_path)
                    app.logger.info(
                        'Получена ссылка для скачивания:'
                        f' {download_link[:50]}...'
                    )
                    results.append({
                        'name': original_filename,
                        'download_url': download_link,
                        'size': len(file_content),
                        'status': 'success'
                    })
                except Exception as e:
                    app.logger.error(
                        f'Ошибка загрузки файла {file.filename}: {str(e)}'
                    )
                    results.append({
                        'name': file.filename,
                        'error': str(e),
                        'status': 'error'
                    })
        except Exception as e:
            app.logger.error(f'Ошибка при загрузке файлов: {e}')
            if not results:
                results = [{
                    'name': f.filename,
                    'error': str(e),
                    'status': 'error'
                } for f in files]
        return results

    def upload_files_sync(self, files):
        """Метод синхронной обертки для асинхронной загрузки."""
        if not files:
            return []

        async def async_upload():
            return await self.upload_files(files)

        try:
            return asyncio.run(async_upload())
        except Exception as e:
            app.logger.error(f'Ошибка в upload_files_sync: {e}')
            return [{
                'name': file.filename,
                'error': str(e),
                'status': 'error'
            } for file in files]


disk_uploader = YaDiskUploader()
