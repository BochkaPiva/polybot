import logging
import os
from pathlib import Path
import PyPDF2
import docx
import textract

from db.models import Document
from search.client import OpenSearchClient

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Class for indexing documents"""
    
    def __init__(self, upload_dir="uploads"):
        """Initialize document indexer"""
        self.upload_dir = upload_dir
        self.client = OpenSearchClient()
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize OpenSearch index"""
        await self.client.create_index()
    
    async def index_document(self, document: Document):
        """Index a document"""
        if document.indexed:
            logger.info(f"Document {document.id} already indexed")
            return True
        
        # Extract text if not already extracted
        if not document.content_text:
            content = await self.extract_text(document.file_path)
            if not content:
                logger.error(f"Failed to extract text from {document.file_path}")
                return False
            
            document.content_text = content
        
        # Create document for indexing
        doc = {
            "id": document.id,
            "title": document.title,
            "content": document.content_text,
            "file_type": document.file_type,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat()
        }
        
        # Index document
        success = await self.client.index_document(document.id, doc)
        if success:
            document.indexed = True
        
        return success
    
    async def extract_text(self, file_path):
        """Extract text from document"""
        full_path = os.path.join(self.upload_dir, file_path)
        
        if not os.path.exists(full_path):
            logger.error(f"File not found: {full_path}")
            return None
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return self._extract_from_pdf(full_path)
            elif file_ext == '.docx':
                return self._extract_from_docx(full_path)
            elif file_ext == '.txt':
                return self._extract_from_txt(full_path)
            else:
                # Use textract for other file types
                return self._extract_with_textract(full_path)
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None
    
    def _extract_from_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path):
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _extract_from_txt(self, file_path):
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_with_textract(self, file_path):
        """Extract text using textract"""
        return textract.process(file_path).decode('utf-8')
    
    async def update_document(self, document: Document):
        """Update indexed document"""
        # Extract text if content changed
        content = await self.extract_text(document.file_path)
        if not content:
            logger.error(f"Failed to extract text from {document.file_path}")
            return False
        
        document.content_text = content
        
        # Create document for indexing
        doc = {
            "title": document.title,
            "content": document.content_text,
            "file_type": document.file_type,
            "updated_at": document.updated_at.isoformat()
        }
        
        # Update document
        return await self.client.update_document(document.id, doc)
    
    async def delete_document(self, document_id):
        """Delete indexed document"""
        return await self.client.delete_document(document_id)
    
    async def close(self):
        """Close client connection"""
        await self.client.close()