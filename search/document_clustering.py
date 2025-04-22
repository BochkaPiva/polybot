from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentClusterer:
    """Класс для кластеризации документов на основе их эмбеддингов"""
    
    def __init__(self, eps: float = 0.3, min_samples: int = 2):
        """
        Инициализация кластеризатора.
        
        Args:
            eps: Максимальное расстояние между двумя точками для включения в один кластер
            min_samples: Минимальное количество точек для формирования кластера
        """
        self.eps = eps
        self.min_samples = min_samples
        self.clusterer = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            metric='cosine'
        )
        
    def cluster_documents(self, embeddings: np.ndarray, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Кластеризация документов на основе их эмбеддингов.
        
        Args:
            embeddings: Матрица эмбеддингов документов shape=(n_documents, embedding_dim)
            documents: Список документов с их метаданными
            
        Returns:
            Список кластеров с информацией о документах
        """
        try:
            logger.info("Начало кластеризации документов...")
            
            # Проверяем входные данные
            if len(embeddings) != len(documents):
                raise ValueError("Количество эмбеддингов не соответствует количеству документов")
                
            if len(embeddings) == 0:
                logger.warning("Нет документов для кластеризации")
                return []
                
            # Выполняем кластеризацию
            labels = self.clusterer.fit_predict(embeddings)
            
            # Формируем кластеры
            clusters = {}
            for idx, label in enumerate(labels):
                if label == -1:  # Шумовые точки
                    continue
                    
                if label not in clusters:
                    clusters[label] = {
                        'cluster_id': int(label),
                        'documents': [],
                        'centroid': None,
                        'keywords': set(),
                        'created_at': datetime.utcnow().isoformat()
                    }
                    
                # Добавляем документ в кластер
                doc_info = {
                    'document_id': documents[idx]['document_id'],
                    'title': documents[idx]['title'],
                    'metadata': documents[idx]['metadata']
                }
                clusters[label]['documents'].append(doc_info)
                
                # Добавляем ключевые слова из метаданных
                if 'keywords' in documents[idx]['metadata']:
                    clusters[label]['keywords'].update(documents[idx]['metadata']['keywords'])
                    
            # Вычисляем центроиды кластеров
            for label in clusters:
                cluster_docs_idx = [i for i, l in enumerate(labels) if l == label]
                cluster_embeddings = embeddings[cluster_docs_idx]
                centroid = np.mean(cluster_embeddings, axis=0)
                clusters[label]['centroid'] = centroid.tolist()
                clusters[label]['keywords'] = list(clusters[label]['keywords'])
                
            logger.info(f"Найдено {len(clusters)} кластеров")
            return list(clusters.values())
            
        except Exception as e:
            logger.error(f"Ошибка при кластеризации документов: {str(e)}", exc_info=True)
            return []
            
    def find_similar_documents(self, query_embedding: np.ndarray, embeddings: np.ndarray,
                             documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск похожих документов на основе косинусного расстояния.
        
        Args:
            query_embedding: Эмбеддинг запроса
            embeddings: Матрица эмбеддингов документов
            documents: Список документов
            top_k: Количество похожих документов для возврата
            
        Returns:
            Список похожих документов с их метаданными и score
        """
        try:
            # Вычисляем косинусное сходство
            similarities = cosine_similarity(query_embedding.reshape(1, -1), embeddings)[0]
            
            # Получаем индексы top-k документов
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Формируем результат
            results = []
            for idx in top_indices:
                doc_info = {
                    'document_id': documents[idx]['document_id'],
                    'title': documents[idx]['title'],
                    'metadata': documents[idx]['metadata'],
                    'similarity_score': float(similarities[idx])
                }
                results.append(doc_info)
                
            return results
            
        except Exception as e:
            logger.error(f"Ошибка при поиске похожих документов: {str(e)}", exc_info=True)
            return []
            
    def get_cluster_summary(self, cluster: Dict[str, Any]) -> Dict[str, Any]:
        """
        Формирует сводную информацию о кластере.
        
        Args:
            cluster: Информация о кластере
            
        Returns:
            Словарь с обобщенной информацией о кластере
        """
        try:
            # Собираем типы документов в кластере
            doc_types = {}
            for doc in cluster['documents']:
                doc_type = doc['metadata'].get('document_type', 'Неизвестный')
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                
            # Определяем основной тип документов
            main_type = max(doc_types.items(), key=lambda x: x[1])[0]
            
            summary = {
                'cluster_id': cluster['cluster_id'],
                'size': len(cluster['documents']),
                'main_document_type': main_type,
                'document_types': doc_types,
                'keywords': cluster['keywords'][:10] if len(cluster['keywords']) > 10 else cluster['keywords'],
                'created_at': cluster['created_at']
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Ошибка при формировании сводки кластера: {str(e)}", exc_info=True)
            return {} 