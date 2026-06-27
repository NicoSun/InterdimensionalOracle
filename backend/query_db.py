#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 15:26:13 2026

@author: nico
"""
import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Tuple


os.environ["HF_HUB_OFFLINE"] = "1"

# Initialize the client and embedding model globally so it loads once on startup
DB_PATH = os.getenv("VECTORDB_PATH", "./rm_vectordb")
COLLECTION_NAME = "rick_and_morty_rag"

client = chromadb.PersistentClient(path=DB_PATH)
local_embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_collection():
    """Helper to fetch the collection."""
    return client.get_collection(
        name=COLLECTION_NAME, 
        embedding_function=local_embedding_model
    )

def search_rag(
    query_text: str, 
    entity_filter: str = None, 
    limit: int = 3, 
    max_distance: float = 1.0
) -> Tuple[List[str], List[Dict]]:
    """
    Queries the local vector database and returns documents and metadatas separately.
    
    :param query_text: The user's semantic search question.
    :param entity_filter: Optional string filter ('character', 'location', 'episode').
    :param limit: Number of top documents to return.
    :param max_distance: Strict threshold for vector similarity.
    :return: A tuple containing (list_of_document_strings, list_of_metadata_dicts)
    """
    collection = get_collection()
    
    # Metadata filter setup
    where_clause = {"entity_type": entity_filter} if entity_filter else None
    
    results = collection.query(
        query_texts=[query_text],
        n_results=limit,
        where=where_clause
    )
    
    filtered_documents = []
    filtered_metadatas = []
    
    # Check if we actually got results back
    if not results or not results['documents'] or not results['documents'][0]:
        return filtered_documents, filtered_metadatas
        
    # Chroma returns lists of lists; unpack the first batch [0]
    for doc, meta, distance in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        if distance <= max_distance:
            filtered_documents.append(doc)
            
            # Add metadata attributes
            meta_copy = dict(meta)
            meta_copy["distance"] = distance
            filtered_metadatas.append(meta_copy)
            
    return filtered_documents, filtered_metadatas

if __name__ == "__main__":
    # Database retrieval tests:
    result = search_rag("Who lives on Hepatitis C?", entity_filter="location")
    # result = search_rag("Show me places or things located inside a human body")
    # result = search_rag("Which episodes featured Poncho?")
    print(result)
