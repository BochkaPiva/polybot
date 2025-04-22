import os
import logging
from pathlib import Path
from typing import Optional
from admin.core.config import settings

logger = logging.getLogger(__name__)

class TextManager:
    def __init__(self):
        # Создаем директории для хранения текстов
        self.raw_text_dir = os.path.join(settings.UPLOAD_DIR, "raw_texts")
        self.cleaned_text_dir = os.path.join(settings.UPLOAD_DIR, "cleaned_texts")
        os.makedirs(self.raw_text_dir, exist_ok=True)
        os.makedirs(self.cleaned_text_dir, exist_ok=True)

    def get_raw_text_path(self, file_hash: str) -> str:
        """Получение пути к файлу с исходным текстом"""
        return os.path.join(self.raw_text_dir, f"{file_hash}.txt")

    def get_cleaned_text_path(self, file_hash: str, version: int = 1) -> str:
        """Получение пути к файлу с очищенным текстом определенной версии"""
        return os.path.join(self.cleaned_text_dir, f"{file_hash}_v{version}.txt")

    def save_raw_text(self, file_hash: str, text: str) -> None:
        """Сохранение исходного текста"""
        try:
            file_path = self.get_raw_text_path(file_hash)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            logger.error(f"Ошибка при сохранении исходного текста: {str(e)}")

    def save_cleaned_text(self, file_hash: str, text: str, version: int = 1) -> None:
        """Сохранение очищенного текста"""
        try:
            file_path = self.get_cleaned_text_path(file_hash, version)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            logger.error(f"Ошибка при сохранении очищенного текста: {str(e)}")

    def get_raw_text(self, file_hash: str) -> Optional[str]:
        """Получение исходного текста"""
        try:
            file_path = self.get_raw_text_path(file_hash)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении исходного текста: {str(e)}")
            return None

    def get_cleaned_text(self, file_hash: str, version: int = 1) -> Optional[str]:
        """Получение очищенного текста определенной версии"""
        try:
            file_path = self.get_cleaned_text_path(file_hash, version)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении очищенного текста: {str(e)}")
            return None

    def get_latest_version(self, file_hash: str) -> int:
        """Получение последней версии очищенного текста"""
        try:
            pattern = f"{file_hash}_v*.txt"
            files = list(Path(self.cleaned_text_dir).glob(pattern))
            if not files:
                return 0
            versions = [int(f.stem.split('_v')[1]) for f in files]
            return max(versions)
        except Exception as e:
            logger.error(f"Ошибка при получении последней версии: {str(e)}")
            return 0

    def delete_texts(self, file_hash: str) -> None:
        """Удаление всех версий текста"""
        try:
            # Удаляем исходный текст
            raw_path = self.get_raw_text_path(file_hash)
            if os.path.exists(raw_path):
                os.remove(raw_path)

            # Удаляем все версии очищенного текста
            pattern = f"{file_hash}_v*.txt"
            for file in Path(self.cleaned_text_dir).glob(pattern):
                os.remove(file)
        except Exception as e:
            logger.error(f"Ошибка при удалении текстов: {str(e)}") 