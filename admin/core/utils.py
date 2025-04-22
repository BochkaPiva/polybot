import os
import uuid
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
import aiofiles
from fastapi import UploadFile
import textract

class FileProcessor:
    def __init__(self, upload_dir: str):
        """Инициализация процессора файлов."""
        self.upload_dir = upload_dir
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        # Инициализируем систему определения MIME-типов
        mimetypes.init()

    def generate_unique_filename(self, original_filename: str) -> str:
        """Генерирует уникальное имя файла, сохраняя оригинальное расширение."""
        ext = os.path.splitext(original_filename)[1]
        return f"{uuid.uuid4().hex}{ext}"

    async def save_file(self, file: UploadFile, system_filename: str) -> str:
        """Асинхронно сохраняет загруженный файл."""
        file_path = os.path.join(self.upload_dir, system_filename)
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return file_path

    def get_mime_type(self, file_path: str) -> str:
        """Определяет MIME-тип файла."""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

    def extract_text(self, file_path: str) -> Optional[str]:
        """Извлекает текст из файла."""
        try:
            text = textract.process(file_path).decode('utf-8')
            return text
        except Exception as e:
            print(f"Ошибка при извлечении текста из {file_path}: {e}")
            return None

    async def process_file(self, file: UploadFile) -> Tuple[str, str, int, Optional[str]]:
        """Обрабатывает загруженный файл и возвращает его метаданные."""
        system_filename = self.generate_unique_filename(file.filename)
        file_path = await self.save_file(file, system_filename)
        
        mime_type = self.get_mime_type(file_path)
        file_size = os.path.getsize(file_path)
        content_text = self.extract_text(file_path)

        return (
            system_filename,
            mime_type,
            file_size,
            content_text
        )

    def delete_file(self, system_filename: str) -> bool:
        """Удаляет файл из файловой системы."""
        try:
            file_path = os.path.join(self.upload_dir, system_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Ошибка при удалении файла {system_filename}: {e}")
            return False 