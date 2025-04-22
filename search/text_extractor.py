import os
from docx import Document
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)

class TextExtractor:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Извлекает текст из файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Извлеченный текст
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return ""
                
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.docx':
                return TextExtractor._extract_from_docx(file_path)
            elif file_ext == '.pdf':
                return TextExtractor._extract_from_pdf(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
            
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Извлекает текст из DOCX файла"""
        try:
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            return ""
            
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Извлекает текст из PDF файла"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return ""

# Создаем глобальный экземпляр
text_extractor = TextExtractor() 