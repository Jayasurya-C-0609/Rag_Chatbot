from embeddings.embedding_model import load_embedding_model
from retriever.hybrid_retriever import load_hybrid_retriever
from retriever.reranker import CrossEncoderReranker
from llm.llm import load_llm
from backend.core.logging import get_logger
import asyncio

logger = get_logger(__name__)

class SystemService:
    def __init__(self):
        self.embedding_model = None
        self.llm = None
        self.reranker = None
        self.retriever = None
        self._lock = asyncio.Lock()

    async def load_models(self):
        async with self._lock:
            if not self.embedding_model:
                logger.info("Loading embedding model...")
                self.embedding_model = load_embedding_model()
            if not self.llm:
                logger.info("Loading LLM...")
                self.llm = load_llm()
            if not self.reranker:
                logger.info("Loading Reranker...")
                self.reranker = CrossEncoderReranker()
            if not self.retriever:
                logger.info("Loading Retriever...")
                self.retriever = load_hybrid_retriever(self.embedding_model)

    async def refresh_retriever(self):
        async with self._lock:
            logger.info("Refreshing Retriever...")
            self.retriever = load_hybrid_retriever(self.embedding_model)
            
system_service = SystemService()
