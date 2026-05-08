# data/gd1_chunker.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_huggingface import HuggingFaceEmbeddings
from config import Config
from data.parser import LegalChunk

class DatabaseBuilder:
    """Xây dựng Qdrant database từ chunks"""
    
    def __init__(self):
        self.client = QdrantClient(path=str(Config.QDRANT_DB_PATH))
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self._create_collection()
    
    def _create_collection(self):
        collections = self.client.get_collections().collections
        if Config.COLLECTION_NAME not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=Config.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=Config.EMBEDDING_DIM,
                    distance=Distance.COSINE
                )
            )
            print(f" Đã tạo collection: {Config.COLLECTION_NAME}")
    
    def build(self, chunks: List[LegalChunk]):
        """Thêm chunks vào database"""
        print(f" Đang tạo embeddings cho {len(chunks)} chunks...")
        
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embeddings.embed_documents(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        
        # Batch insert
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            points = []
            for idx, chunk in enumerate(batch):
                point_id = i + idx
                points.append(PointStruct(
                    id=point_id,
                    vector=chunk.embedding,
                    payload={
                        "id": chunk.id,
                        "content": chunk.content,
                        "title": chunk.title,
                        "chapter": chunk.chapter,
                        "article": chunk.article,
                        "clause": chunk.clause,
                        "keywords": ",".join(chunk.keywords),
                        "chunk_type": chunk.chunk_type
                    }
                ))
            self.client.upsert(collection_name=Config.COLLECTION_NAME, points=points)
            print(f"   Đã thêm {min(i+batch_size, len(chunks))}/{len(chunks)} points")
        
        # Lưu metadata
        self._save_metadata(chunks)
        print(f" Đã thêm {len(chunks)} chunks vào Qdrant")
    
    def _save_metadata(self, chunks: List[LegalChunk]):
        metadata_dir = Path(Config.METADATA_PATH)
        metadata_dir.mkdir(exist_ok=True)
        
        chunks_data = []
        for chunk in chunks:
            chunks_data.append({
                "id": chunk.id,
                "content_preview": chunk.content[:200],
                "title": chunk.title,
                "chapter": chunk.chapter,
                "article": chunk.article,
                "clause": chunk.clause,
                "keywords": chunk.keywords,
                "chunk_type": chunk.chunk_type
            })
        
        with open(metadata_dir / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        print(f" Đã lưu metadata vào {metadata_dir}")