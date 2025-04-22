import re
from typing import List, Set
import logging

logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self):
        # Паттерны для удаления
        self.patterns = [
            r'^Страница \d+ из \d+$',  # Номера страниц
            r'^\d+$',  # Одиночные цифры
            r'^\s*$',  # Пустые строки
            r'^[^\w\s]+$',  # Строки только из спецсимволов
        ]
        
        # Слова для удаления
        self.stop_words = {
            'город', 'область', 'район', 'улица', 'дом', 'корпус', 'квартира',
            'телефон', 'факс', 'email', 'сайт', 'www', 'http', 'https',
            'страница', 'лист', 'листов', 'страниц', 'из', 'всего'
        }
        
        # Регулярные выражения для колонтитулов
        self.header_footer_patterns = [
            r'^.*\d{2}\.\d{2}\.\d{4}.*$',  # Даты в начале строки
            r'^.*\d{2}:\d{2}:\d{2}.*$',    # Время в начале строки
        ]

    def clean_text(self, text: str) -> str:
        """Очистка текста от мусора"""
        try:
            # Разбиваем текст на строки
            lines = text.split('\n')
            cleaned_lines = []
            
            # Очищаем каждую строку
            for line in lines:
                line = line.strip()
                
                # Пропускаем строки, соответствующие паттернам
                if any(re.match(pattern, line) for pattern in self.patterns):
                    continue
                    
                # Пропускаем строки с колонтитулами
                if any(re.match(pattern, line) for pattern in self.header_footer_patterns):
                    continue
                    
                # Удаляем стоп-слова
                words = line.split()
                cleaned_words = [word for word in words if word.lower() not in self.stop_words]
                
                if cleaned_words:
                    cleaned_lines.append(' '.join(cleaned_words))
            
            # Объединяем строки обратно
            cleaned_text = '\n'.join(cleaned_lines)
            
            # Удаляем множественные пробелы и переносы строк
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            # Нормализуем текст (приводим к нижнему регистру)
            cleaned_text = cleaned_text.lower()
            
            return cleaned_text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при очистке текста: {str(e)}")
            return text  # Возвращаем оригинальный текст в случае ошибки

    def is_duplicate(self, text1: str, text2: str, threshold: float = 0.9) -> bool:
        """Проверка на дубликаты текста с использованием простого сравнения"""
        try:
            # Нормализуем тексты
            text1 = self.clean_text(text1)
            text2 = self.clean_text(text2)
            
            # Разбиваем на слова
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            # Вычисляем коэффициент схожести
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return False
                
            similarity = intersection / union
            return similarity >= threshold
            
        except Exception as e:
            logger.error(f"Ошибка при проверке дубликатов: {str(e)}")
            return False 