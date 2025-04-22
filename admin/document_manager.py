import logging
from typing import Optional
from opensearchpy import OpenSearch
from .models.document import Document
from search.cluster_storage import ClusterStorage

logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self, opensearch_client: OpenSearch):
        self.opensearch_client = opensearch_client
        self.cluster_storage = ClusterStorage(opensearch_client)
        
    async def delete_document(self, document_id: int) -> bool:
        """
        Каскадное удаление документа и всей связанной информации.
        
        Args:
            document_id: ID документа для удаления
            
        Returns:
            bool: True если удаление прошло успешно, False в случае ошибки
        """
        try:
            # 1. Получаем документ из БД
            document = await Document.get(document_id)
            if not document:
                logger.warning(f"Документ с ID {document_id} не найден")
                return False
                
            # 2. Получаем cluster_id документа из OpenSearch
            try:
                doc_response = self.opensearch_client.get(
                    index="documents",
                    id=str(document_id)
                )
                cluster_id = doc_response["_source"].get("cluster_id")
            except Exception as e:
                logger.error(f"Ошибка при получении cluster_id: {str(e)}")
                cluster_id = None
                
            # 3. Удаляем документ из индекса documents в OpenSearch
            try:
                self.opensearch_client.delete(
                    index="documents",
                    id=str(document_id)
                )
                logger.info(f"Документ {document_id} удален из индекса documents")
            except Exception as e:
                logger.error(f"Ошибка при удалении из индекса documents: {str(e)}")
                
            # 4. Если есть cluster_id, обновляем кластер
            if cluster_id is not None:
                try:
                    # Получаем текущий кластер
                    cluster = await self.cluster_storage.get_cluster(cluster_id)
                    if cluster:
                        # Удаляем документ из списка документов кластера
                        cluster["documents"] = [
                            doc for doc in cluster["documents"]
                            if doc["document_id"] != document_id
                        ]
                        
                        if len(cluster["documents"]) > 0:
                            # Обновляем кластер
                            await self.cluster_storage.update_cluster(cluster_id, cluster)
                            logger.info(f"Документ удален из кластера {cluster_id}")
                        else:
                            # Если кластер пустой, удаляем его
                            await self.cluster_storage.delete_cluster(cluster_id)
                            logger.info(f"Пустой кластер {cluster_id} удален")
                except Exception as e:
                    logger.error(f"Ошибка при обновлении кластера: {str(e)}")
                    
            # 5. Удаляем физический файл
            try:
                if document.system_filename:
                    import os
                    file_path = os.path.join("uploads", document.system_filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Физический файл {file_path} удален")
            except Exception as e:
                logger.error(f"Ошибка при удалении физического файла: {str(e)}")
                
            # 6. Удаляем запись из БД
            await document.delete()
            logger.info(f"Запись о документе {document_id} удалена из БД")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при каскадном удалении документа {document_id}: {str(e)}", exc_info=True)
            return False 