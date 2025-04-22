import logging
from typing import List, Dict, Any
import yake
import re

logger = logging.getLogger(__name__)

class KeywordExtractor:
    """Класс для извлечения ключевых фраз из текста с использованием YAKE"""
    
    def __init__(self, 
                 language: str = "ru",
                 max_keywords: int = 10,
                 deduplication_threshold: float = 0.9,
                 max_ngram_size: int = 3,
                 min_word_length: int = 3):
        """
        Инициализация экстрактора ключевых слов.
        
        Args:
            language: Язык текста
            max_keywords: Максимальное количество ключевых слов
            deduplication_threshold: Порог для дедупликации ключевых слов
            max_ngram_size: Максимальный размер n-грамм
            min_word_length: Минимальная длина слова
        """
        self.language = language
        self.max_keywords = max_keywords
        self.deduplication_threshold = deduplication_threshold
        self.max_ngram_size = max_ngram_size
        self.min_word_length = min_word_length
            
        # Инициализируем YAKE
        self.extractor = yake.KeywordExtractor(
            lan=language,
            n=max_ngram_size,
            dedupLim=deduplication_threshold,
            dedupFunc='seqm',
            windowsSize=1,
            top=max_keywords,
            features=None
        )
        
    def _clean_text(self, text: str) -> str:
        """
        Очистка текста перед извлечением ключевых слов.
        
        Args:
            text: Исходный текст
            
        Returns:
            Очищенный текст
        """
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Удаляем номера разделов и пунктов
        text = re.sub(r'\d+\.(\d+\.)*\s*', '', text)
        
        # Удаляем множественные пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем специальные символы, оставляя только буквы, цифры и пробелы
        text = re.sub(r'[^а-яёa-z0-9\s]', ' ', text)
        
        return text.strip()
        
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Разбиение текста на предложения.
        
        Args:
            text: Текст для разбиения
            
        Returns:
            Список предложений
        """
        # Очищаем текст
        text = self._clean_text(text)
        
        # Разбиваем по точкам, восклицательным и вопросительным знакам
        sentences = re.split(r'[.!?]+', text)
        
        # Удаляем пустые предложения и лишние пробелы
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Фильтруем короткие предложения
        sentences = [s for s in sentences if len(s.split()) >= 3]
        
        return sentences
        
    def _filter_keywords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрация и нормализация ключевых слов.
        
        Args:
            keywords: Список ключевых слов
            
        Returns:
            Отфильтрованный список ключевых слов
        """
        filtered = []
        seen = set()
        
        for kw in keywords:
            keyword = kw["keyword"]
            
            # Пропускаем слишком короткие слова
            if len(keyword) < self.min_word_length:
                continue
                
            # Пропускаем дубликаты
            if keyword in seen:
                continue
                
            # Пропускаем ключевые слова, состоящие только из цифр
            if keyword.isdigit():
                continue
                
            # Пропускаем ключевые слова с повторяющимися словами
            words = keyword.split()
            if len(words) != len(set(words)):
                continue
                
            filtered.append(kw)
            seen.add(keyword)
            
        return filtered
        
    def extract_keywords(self, text: str) -> List[Dict[str, Any]]:
        """
        Извлечение ключевых слов из текста.
        
        Args:
            text: Текст для анализа
            
        Returns:
            Список словарей с ключевыми словами и их оценками
        """
        try:
            # Разбиваем текст на предложения
            sentences = self._split_into_sentences(text)
            
            # Извлекаем ключевые слова для каждого предложения
            all_keywords = []
            for sentence in sentences:
                keywords = self.extractor.extract_keywords(sentence)
                all_keywords.extend(keywords)
                
            # Сортируем и дедуплицируем ключевые слова
            unique_keywords = {}
            for keyword, score in all_keywords:
                if keyword not in unique_keywords or score < unique_keywords[keyword]:
                    unique_keywords[keyword] = score
                    
            # Сортируем по score (чем меньше, тем лучше)
            sorted_keywords = sorted(
                [{"keyword": k, "score": s} for k, s in unique_keywords.items()],
                key=lambda x: x["score"]
            )[:self.max_keywords]
            
            # Фильтруем и нормализуем ключевые слова
            filtered_keywords = self._filter_keywords(sorted_keywords)
            
            logger.info(f"Извлечено {len(filtered_keywords)} ключевых слов")
            return filtered_keywords
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении ключевых слов: {str(e)}", exc_info=True)
            return []
            
    def extract_keywords_for_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлечение ключевых слов для документа.
        
        Args:
            document: Словарь с информацией о документе
            
        Returns:
            Обновленный словарь с добавленными ключевыми словами
        """
        try:
            # Извлекаем ключевые слова из заголовка и содержимого
            title_keywords = self.extract_keywords(document.get("title", ""))
            content_keywords = self.extract_keywords(document.get("content", ""))
            
            # Объединяем и сортируем ключевые слова
            all_keywords = title_keywords + content_keywords
            unique_keywords = {}
            
            for kw in all_keywords:
                keyword = kw["keyword"]
                if keyword not in unique_keywords or kw["score"] < unique_keywords[keyword]["score"]:
                    unique_keywords[keyword] = kw
                    
            # Сортируем по score и берем топ-N
            sorted_keywords = sorted(
                unique_keywords.values(),
                key=lambda x: x["score"]
            )[:self.max_keywords]
            
            # Обновляем документ
            document["keywords"] = sorted_keywords
            document["tags"] = [kw["keyword"] for kw in sorted_keywords]
            
            logger.info(f"Извлечено {len(sorted_keywords)} ключевых слов для документа {document.get('id')}")
            return document
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении ключевых слов для документа: {str(e)}", exc_info=True)
            return document 