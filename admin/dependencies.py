from opensearchpy import OpenSearch
from .document_manager import DocumentManager

def get_opensearch_client():
    """Получение клиента OpenSearch"""
    return OpenSearch(
        hosts=['http://localhost:9200'],
        http_auth=('admin', 'admin'),
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False
    )

def get_document_manager(opensearch_client: OpenSearch = Depends(get_opensearch_client)) -> DocumentManager:
    """Получение менеджера документов"""
    return DocumentManager(opensearch_client) 