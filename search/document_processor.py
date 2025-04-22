from typing import List, Dict, Any, Optional
import re
from pathlib import Path
import logging
from datetime import datetime

class DocumentProcessor:
    """Класс для обработки и подготовки документов к индексации в OpenSearch."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Инициализация процессора документов.
        
        Args:
            chunk_size: Размер чанка в символах
            overlap: Размер перекрытия между чанками в символах
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = logging.getLogger(__name__)
        
    def clean_text(self, text: str) -> str:
        """
        Очистка текста от лишних символов и форматирования.
        
        Args:
            text: Исходный текст
            
        Returns:
            Очищенный текст
        """
        # Удаляем множественные пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        # Удаляем специальные символы, оставляя только буквы, цифры и основные знаки препинания
        text = re.sub(r'[^\w\s.,!?;:()\-–—]', ' ', text)
        # Удаляем множественные пробелы после очистки
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Разбиение текста на чанки с перекрытием.
        
        Args:
            text: Исходный текст
            
        Returns:
            Список чанков
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # Определяем конец текущего чанка
            end = start + self.chunk_size
            
            # Если это не последний чанк, ищем ближайший конец предложения
            if end < len(text):
                # Ищем ближайшую точку, восклицательный или вопросительный знак
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                if sentence_end != -1:
                    end = sentence_end + 1
            
            # Добавляем чанк
            chunks.append(text[start:end].strip())
            
            # Определяем начало следующего чанка с учетом перекрытия
            start = end - self.overlap if end < len(text) else end
        
        return chunks
    
    async def process_document(self, document_id: int, title: str, content: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Обработка документа и подготовка к индексации.
        
        Args:
            document_id: ID документа
            title: Заголовок документа
            content: Содержимое документа
            metadata: Дополнительные метаданные
            
        Returns:
            Список чанков документа
        """
        try:
            self.logger.info(f"Начало обработки документа {document_id}")
            
            if not content:
                self.logger.error(f"Пустое содержимое документа {document_id}")
                return []
                
            # Очищаем текст
            self.logger.info("Очистка текста...")
            cleaned_content = self.clean_text(content)
            if not cleaned_content:
                self.logger.error(f"После очистки текст документа {document_id} пуст")
                return []
                
            # Разбиваем на чанки
            self.logger.info("Разбиение на чанки...")
            chunks = self.split_into_chunks(cleaned_content)
            if not chunks:
                self.logger.error(f"Не удалось разбить документ {document_id} на чанки")
                return []
                
            self.logger.info(f"Документ разбит на {len(chunks)} чанков")
            
            # Подготавливаем чанки для индексации
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunk = {
                    "document_id": document_id,
                    "chunk_id": i,
                    "title": title,
                    "content": chunk,
                    "metadata": metadata or {},
                    "timestamp": datetime.utcnow().isoformat()
                }
                processed_chunks.append(processed_chunk)
                
            self.logger.info(f"Документ {document_id} успешно обработан")
            return processed_chunks
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке документа {document_id}: {str(e)}", exc_info=True)
            return [] 