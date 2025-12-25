import asyncio
import re
import os
from http import HTTPStatus

import aiohttp

from settings import Config


HEADERS = {
    'Accept': 'application/json',
    'Authorization': f'OAuth {Config.DISK_TOKEN}'
}


class YaDiskUploader:
    """Класс для асинхронной загрузки файлов на Яндекс диск."""

    base_url = Config.YANDEX_DISK_BASE_URL

    async def _make_request(self, method, endpoint, **kwargs):
        """Метод для выполнения HTTP-запросов."""
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.request(
                method,
                f'{self.base_url}/{endpoint}',
                **kwargs
            ) as response:
                response.raise_for_status()
                if response.status == HTTPStatus.NO_CONTENT:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message='No content'
                    )
                return await response.json()

    async def create_folder(self, folder_path):
        """Метод создания папки на Яндекс диске."""
        try:
            await self._make_request('PUT', f'resources?path={folder_path}')
        except aiohttp.ClientResponseError as e:
            if e.status != HTTPStatus.CONFLICT:
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
        return re.sub(r'[^\w\-\.]', '_', name) + ext

    async def _process_single_file(self, file, folder_name):
        """Обработка одного файла."""
        file_path = (
            f'{folder_name}/'
            f'{self._make_filename_safe(file.filename)}'
        )
        file_content = file.read()

        await self.upload_file(
            await self.get_upload_link(file_path),
            file_content
        )

        return await self.get_download_link(file_path)

    async def upload_files(self, files):
        """Асинхронная загрузка файлов."""
        folder_name = f'app:/{Config.YANDEX_DISK_FOLDER}'
        return [
            await self._process_single_file(
                file,
                folder_name
            )
            for file in files
        ]

    def upload_files_sync(self, files):
        """Метод синхронной обертки для асинхронной загрузки."""
        async def async_upload():
            return await self.upload_files(files)

        return asyncio.run(async_upload())


disk_uploader = YaDiskUploader()
