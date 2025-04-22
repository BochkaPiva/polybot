import torch
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self):
        """Инициализация модели для генерации эмбеддингов"""
        try:
            self.model = SentenceTransformer('sberbank-ai/sbert_large_nlu_ru')
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(self.device)
            logger.info(f"Модель для эмбеддингов загружена, используется устройство: {self.device}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {str(e)}")
            raise

    def generate_embedding(self, text: str) -> list:
        """Генерация эмбеддинга для текста"""
        try:
            # Генерируем эмбеддинг
            embedding = self.model.encode(text, convert_to_tensor=True)
            # Конвертируем в список для сериализации
            return embedding.cpu().numpy().tolist()
        except Exception as e:
            logger.error(f"Ошибка при генерации эмбеддинга: {str(e)}")
            raise

# Создаем глобальный экземпляр генератора
embedding_generator = EmbeddingGenerator() 