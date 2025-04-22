from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from opensearchpy import OpenSearch, helpers
import json
import numpy as np

logger = logging.getLogger(__name__)

class ClusterStorage:
    """Класс для хранения информации о кластерах в OpenSearch"""
    
    def __init__(self, client: OpenSearch, index_name: str = "clusters"):
        """
        Инициализация хранилища кластеров.
        
        Args:
            client: Клиент OpenSearch
            index_name: Имя индекса для хранения кластеров
        """
        self.client = client
        self.index_name = index_name
        
    async def init_index(self):
        """Инициализация индекса для хранения кластеров"""
        try:
            # Проверяем существование индекса
            if not self.client.indices.exists(index=self.index_name):
                # Создаем маппинг для индекса
                mapping = {
                    "mappings": {
                        "properties": {
                            "cluster_id": {"type": "integer"},
                            "documents": {
                                "type": "nested",
                                "properties": {
                                    "document_id": {"type": "integer"},
                                    "title": {"type": "text"},
                                    "metadata": {"type": "object"}
                                }
                            },
                            "centroid": {"type": "float"},
                            "keywords": {"type": "keyword"},
                            "main_document_type": {"type": "keyword"},
                            "document_types": {"type": "object"},
                            "size": {"type": "integer"},
                            "created_at": {"type": "date"}
                        }
                    }
                }
                
                # Создаем индекс
                self.client.indices.create(
                    index=self.index_name,
                    body=mapping
                )
                logger.info(f"Создан индекс {self.index_name}")
                
        except Exception as e:
            logger.error(f"Ошибка при инициализации индекса: {str(e)}", exc_info=True)
            
    async def store_clusters(self, clusters: List[Dict[str, Any]]) -> bool:
        """
        Сохранение информации о кластерах.
        
        Args:
            clusters: Список кластеров для сохранения
            
        Returns:
            True если сохранение успешно, False в случае ошибки
        """
        try:
            # Подготавливаем данные для bulk операции
            actions = []
            for cluster in clusters:
                # Получаем сводную информацию о кластере
                cluster_doc = {
                    "_index": self.index_name,
                    "_id": f"cluster_{cluster['cluster_id']}",
                    "_source": {
                        "cluster_id": cluster['cluster_id'],
                        "documents": cluster['documents'],
                        "centroid": cluster['centroid'],
                        "keywords": cluster['keywords'],
                        "created_at": cluster['created_at']
                    }
                }
                actions.append(cluster_doc)
                
            if actions:
                # Выполняем bulk операцию
                helpers.bulk(self.client, actions)
                logger.info(f"Сохранено {len(actions)} кластеров")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении кластеров: {str(e)}", exc_info=True)
            return False
            
    async def get_cluster(self, cluster_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение информации о кластере по его ID.
        
        Args:
            cluster_id: ID кластера
            
        Returns:
            Информация о кластере или None в случае ошибки
        """
        try:
            response = self.client.get(
                index=self.index_name,
                id=f"cluster_{cluster_id}"
            )
            return response["_source"]
            
        except Exception as e:
            logger.error(f"Ошибка при получении кластера {cluster_id}: {str(e)}", exc_info=True)
            return None
            
    async def find_cluster_for_embedding(self, embedding: List[float], min_score: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        Поиск ближайшего кластера для эмбеддинга.
        
        Args:
            embedding: Эмбеддинг для поиска
            min_score: Минимальный score для включения в кластер
            
        Returns:
            Информация о ближайшем кластере или None
        """
        try:
            # Получаем все кластеры
            query = {
                "query": {
                    "match_all": {}
                },
                "size": 100  # Ограничиваем количество результатов
            }
            
            response = self.client.search(
                index=self.index_name,
                body=query
            )
            
            if not response["hits"]["hits"]:
                return None
                
            # Вычисляем косинусное сходство для каждого кластера
            best_cluster = None
            best_score = -1
            
            for hit in response["hits"]["hits"]:
                cluster = hit["_source"]
                centroid = cluster.get("centroid")
                if not centroid:
                    continue
                    
                # Вычисляем косинусное сходство
                score = np.dot(embedding, centroid) / (
                    np.linalg.norm(embedding) * np.linalg.norm(centroid)
                )
                
                if score > best_score:
                    best_score = score
                    best_cluster = cluster
                    
            if best_score >= min_score:
                return best_cluster
                
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при поиске кластера: {str(e)}", exc_info=True)
            return None
            
    async def update_cluster(self, cluster_id: int, updates: Dict[str, Any]) -> bool:
        """
        Обновление информации о кластере.
        
        Args:
            cluster_id: ID кластера
            updates: Словарь с обновлениями
            
        Returns:
            True если обновление успешно, False в случае ошибки
        """
        try:
            self.client.update(
                index=self.index_name,
                id=f"cluster_{cluster_id}",
                body={"doc": updates}
            )
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении кластера {cluster_id}: {str(e)}", exc_info=True)
            return False
            
    async def delete_cluster(self, cluster_id: int) -> bool:
        """
        Удаление кластера.
        
        Args:
            cluster_id: ID кластера
            
        Returns:
            True если удаление успешно, False в случае ошибки
        """
        try:
            self.client.delete(
                index=self.index_name,
                id=f"cluster_{cluster_id}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при удалении кластера {cluster_id}: {str(e)}", exc_info=True)
            return False 