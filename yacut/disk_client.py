import asyncio
import re
import os
from http import HTTPStatus

import aiohttp


BASE_URL = os.getenv('YANDEX_DISK_BASE_URL')
DEFAULT_HEADERS = {'Accept': 'application/json'}


class YaDiskUploader:
    """Класс для асинхронной загрузки файлов на Яндекс диск."""

    def __init__(self):
        token = os.getenv('DISK_TOKEN')
        self.base_url = 'https://cloud-api.yandex.net/v1/disk'
        self.headers = {**DEFAULT_HEADERS, 'Authorization': f'OAuth {token}'}

    async def _make_request(self, method, endpoint, **kwargs):
        """Метод для выполнения HTTP-запросов."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.request(
                method,
                f'{self.base_url}/{endpoint}',
                **kwargs
            ) as response:
                response.raise_for_status()
                if response.status == HTTPStatus.NO_CONTENT:
                    return None
                return await response.json()

    async def create_folder(self, folder_path):
        """Метод создания папки на Яндекс диске."""
        try:
            await self._make_request('PUT', f'resources?path={folder_path}')
            return True
        except aiohttp.ClientResponseError as e:
            if e.status == HTTPStatus.CONFLICT:
                return True

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

        for file in files:
            original_filename = file.filename
            file_content = file.read()
            if not file_content:
                raise ValueError('Файл пустой')
            file_path = (
                f'{folder_name}/'
                f'{self._make_filename_safe(original_filename)}'
            )
            await self.upload_file(
                await self.get_upload_link(file_path),
                file_content
            )
            results.append({
                'name': original_filename,
                'download_url': await self.get_download_link(file_path),
            })
        return results

    def upload_files_sync(self, files):
        """Метод синхронной обертки для асинхронной загрузки."""
        async def async_upload():
            return await self.upload_files(files)

        return asyncio.run(async_upload())


disk_uploader = YaDiskUploader()
