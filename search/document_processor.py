from typing import List, Dict, Any, Optional, Tuple
import re
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Класс для обработки документов"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Инициализация процессора документов.
        
        Args:
            chunk_size: Размер чанка в символах
            overlap: Размер перекрытия между чанками в символах
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Регулярные выражения для очистки текста
        self.header_pattern = re.compile(r'^АКЦИОНЕРНОЕ ОБЩЕСТВО.*?СИСТЕМА МЕНЕДЖМЕНТА.*?\n', re.DOTALL | re.IGNORECASE)
        self.page_number_pattern = re.compile(r'^\s*\d+\s*$', re.MULTILINE)
        self.signature_pattern = re.compile(r'^\s*[А-Я][а-я]+\s+[А-Я][а-я]+\s*$', re.MULTILINE)
        self.empty_line_pattern = re.compile(r'^\s*$', re.MULTILINE)
        
        # Регулярные выражения для извлечения структуры
        self.section_pattern = re.compile(r'^\d+\.\s+[А-Яа-я\s]+$', re.MULTILINE)
        self.subsection_pattern = re.compile(r'^\d+\.\d+\.\s+[А-Яа-я\s]+$', re.MULTILINE)
        self.list_item_pattern = re.compile(r'^[-\d\)]\s+[А-Яа-я\s]+$', re.MULTILINE)
        
    def clean_text(self, text: str) -> str:
        """
        Очищает текст от шапок, подписей, нумерации страниц и лишних пробелов.
        
        Args:
            text: Исходный текст
            
        Returns:
            Очищенный текст
        """
        if not text:
            return ""
            
        # Удаляем шапку документа
        text = self.header_pattern.sub('', text)
        
        # Удаляем номера страниц
        text = self.page_number_pattern.sub('', text)
        
        # Удаляем подписи
        text = self.signature_pattern.sub('', text)
        
        # Удаляем пустые строки
        text = self.empty_line_pattern.sub('', text)
        
        # Заменяем множественные пробелы и переносы строк на одиночные
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем специальные символы, оставляя только буквы, цифры и базовую пунктуацию
        text = re.sub(r'[^\w\s\.,!?-]', '', text)
        
        # Удаляем пробелы в начале и конце
        text = text.strip()
        
        return text
        
    def _preprocess_text(self, text: str) -> str:
        """
        Предварительная обработка текста для извлечения структуры и метаданных.
        Сохраняет форматирование и переносы строк, в отличие от clean_text().
        """
        if not text:
            return ""
            
        # Удаляем множественные пробелы внутри строк
        lines = []
        for line in text.split('\n'):
            line = re.sub(r'\s+', ' ', line.strip())
            if line:
                lines.append(line)
                
        return '\n'.join(lines)
        
    def extract_structure(self, text: str) -> Dict[str, Any]:
        """
        Извлекает структуру документа (заголовки, подзаголовки, списки).
        
        Args:
            text: Исходный текст
            
        Returns:
            Словарь с информацией о структуре документа
        """
        structure = {
            'sections': [],
            'subsections': [],
            'lists': []
        }
        
        if not text:
            return structure
            
        # Предварительная обработка текста
        text = self._preprocess_text(text)
        
        # Разбиваем текст на строки
        lines = text.split('\n')
        
        current_section = None
        current_subsection = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Проверяем на раздел (например, "1. Общие положения")
            if re.match(r'^\d+\.\s+[А-Яа-я]', line):
                current_section = line
                structure['sections'].append(line)
                continue
                
            # Проверяем на подраздел (например, "1.1. Область применения")
            if re.match(r'^\d+\.\d+\.\s+[А-Яа-я]', line):
                current_subsection = line
                structure['subsections'].append(line)
                continue
                
            # Проверяем на элемент списка
            if re.match(r'^[-•]\s+[А-Яа-я]', line) or re.match(r'^\d+\)\s+[А-Яа-я]', line):
                structure['lists'].append(line)
                
        return structure
        
    def extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """
        Извлекает метаданные из текста документа.
        
        Args:
            text: Исходный текст
            filename: Имя файла
            
        Returns:
            Словарь с метаданными документа
        """
        metadata = {
            'filename': filename,
            'document_type': self._detect_document_type(filename, text),
            'application_area': self._extract_application_area(text),
            'date': self._extract_date(text),
            'structure': self.extract_structure(text)
        }
        
        return metadata
        
    def _detect_document_type(self, filename: str, text: str) -> str:
        """Определяет тип документа на основе имени файла и содержимого"""
        # Проверяем имя файла
        filename_lower = filename.lower()
        if 'положение' in filename_lower:
            return 'Положение'
        if 'инструкция' in filename_lower:
            return 'Инструкция'
        if 'регламент' in filename_lower:
            return 'Регламент'
            
        # Проверяем содержимое
        text_lower = text.lower()
        if 'положение' in text_lower:
            return 'Положение'
        if 'инструкция' in text_lower:
            return 'Инструкция'
        if 'регламент' in text_lower:
            return 'Регламент'
            
        return 'Документ'
        
    def _extract_application_area(self, text: str) -> str:
        """Извлекает область применения документа"""
        # Предварительная обработка текста
        text = self._preprocess_text(text)
        
        # Ищем раздел "Область применения"
        patterns = [
            r'1\.1\.\s+Область применения\s*(.*?)(?=\d+\.\d+\.|\Z)',
            r'Область применения\s*(.*?)(?=\d+\.|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                area_text = match.group(1).strip()
                return area_text
                
        return ''
        
    def _extract_date(self, text: str) -> Optional[str]:
        """Извлекает дату документа"""
        # Предварительная обработка текста
        text = self._preprocess_text(text)
        
        # Ищем дату в различных форматах
        patterns = [
            r'\b\d{2}\.\d{2}\.\d{4}\b',  # DD.MM.YYYY
            r'\b\d{4}\b'  # YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
                
        return None
        
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
            logger.info(f"Начало обработки документа {document_id}")
            
            if not content:
                logger.error(f"Пустое содержимое документа {document_id}")
                return []
                
            # Очищаем текст
            logger.info("Очистка текста...")
            cleaned_content = self.clean_text(content)
            if not cleaned_content:
                logger.error(f"После очистки текст документа {document_id} пуст")
                return []
                
            # Извлекаем метаданные
            logger.info("Извлечение метаданных...")
            extracted_metadata = self.extract_metadata(cleaned_content, title)
            if metadata:
                extracted_metadata.update(metadata)
                
            # Разбиваем на чанки
            logger.info("Разбиение на чанки...")
            chunks = self.split_into_chunks(cleaned_content)
            if not chunks:
                logger.error(f"Не удалось разбить документ {document_id} на чанки")
                return []
                
            logger.info(f"Документ разбит на {len(chunks)} чанков")
            
            # Подготавливаем чанки для индексации
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunk = {
                    "document_id": document_id,
                    "chunk_id": i,
                    "title": title,
                    "content": chunk,
                    "metadata": extracted_metadata,
                    "timestamp": datetime.utcnow().isoformat()
                }
                processed_chunks.append(processed_chunk)
                
            logger.info(f"Документ {document_id} успешно обработан")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Ошибка при обработке документа {document_id}: {str(e)}", exc_info=True)
            return [] 