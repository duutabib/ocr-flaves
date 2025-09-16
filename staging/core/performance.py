import asyncio
from typing import Dict, Any,List, Optional 
from concurrent.futures import ThreadPoolExecutor
import redis
import pickle
import hashlib
from queue import Queue
import threading



class DocumentCache:
    """Redis-based caching for processed documents"""

    def __init__(self, redis_host='localhost', redis_port=6379, ttl=3600):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.ttl = ttl


    def _generate_cache_key(self, document_has:str, processing_params:Dict[str, Any]) -> str:
        """Generate unique cache key for document + parameters"""
        params_str = json.dumps(processing_params, sort_keys=True)
        combined = f"{document_hash}:{params_str}"
        return hashlib.md5(combined.encode()).hexdigest()


    def get(self, document_hash:str, processing_params:Dict[str, Any]) -> Optional[Dict]:
        """Retrieve cached result if available"""
        cache_key = self._generate_cache_key(document_hash, processing_params)
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            return pickle.loads(cached_data)
        return None

    
    def set(self, document_hash:str, processing_params:Dict, result:Dict) -> None:
        """Cache processing result"""
        cache_key = self._generate_cache_key(document_hash, processing_params)
        self.redis_client.setex(
            cache_key,
            self.ttl,
            pickle.dumps(result)
        )
        


class AsyncDocumentProcessor:
    """Asynchronous document processing with queue"""

    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.processing_queue = Queue()
        self.results = {}
        self.cache = DocumentCache()

    async def process_batch(self, documents: List[Dict])-> List[Dict]:
        """Process multiple documents concurrently"""
        loop = asyncio.get_event_loop()

        # check cache first
        tasks = []
        for doc in documents:
            cached_result = self.cache.get(doc['hash'], doc.get('params', {}))
            if cached_result:
                tasks.append(asyncio.create_task(self._return_cached(cached_result)))
            else:
                tasks.append(
                    loop.run_in_executor(
                        self.executor,
                        self._process_single,
                        doc
                    )
                )
        results = await asyncio.gather(*tasks)
        
        # Cache new results
        for doc, result in zip(documents, results):
            if not results.get('from_cache'):
                self.cache.set(doc['hash'], doc.get('params', {}), result)

        return results

    async def _return_cached(self, result:Dict) -> Dict:
        """ Return cached result"""
        result['from_cache'] = True
        return result

    def _process_single(self, document:Dict) -> Dict:
        """ Process single document (CPU-intensive task)"""
        # Your actual OCR processing logic here
        pass