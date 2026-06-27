#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 16:05:26 2026

@author: nico
"""
import json
import re
import chromadb
from chromadb.utils import embedding_functions


def extract_id(url_str):
    if not url_str: 
        return None
    match = re.search(r'/(\d+)$', url_str)
    return match.group(1) if match else None

def generate_and_load_rag_docs():
    print("Loading data cache...")
    with open("db_json//rick_and_morty_raw_cache.json", "r", encoding="utf-8") as f:
        cache = json.load(f)
        
    characters = cache["characters"]
    locations = cache["locations"]
    episodes = cache["episodes"]
    
    documents = []
    metadatas = []
    ids = []
    
    # 2. Process LOCATIONS
    print("Processing Locations...")
    for loc_id, loc in locations.items():
        resident_names = [
            characters[char_id]["name"] 
            for url in loc["residents"] 
            if (char_id := extract_id(url)) in characters
        ]
        
        residents_str = ", ".join(resident_names) if resident_names else "none"
        text_chunk = f"Location: {loc['name']}. Type: {loc['type']}. Dimension: {loc['dimension']}. Known residents: {residents_str}."
        
        documents.append(text_chunk)
        ids.append(f"location_{loc_id}")
        metadatas.append({
            "id": int(loc_id),
            "entity_type": "location",
            "name": loc["name"],
            "type_or_species": loc["type"]
        })

    # 3. Process EPISODES
    print("Processing Episodes...")
    for ep_id, ep in episodes.items():
        character_names = [
            characters[char_id]["name"] 
            for url in ep["characters"] 
            if (char_id := extract_id(url)) in characters
        ]
        
        chars_str = ", ".join(character_names) if character_names else "none"
        text_chunk = f"Episode: {ep['name']}. Air Date: {ep['air_date']}. Code: {ep['episode']}. Characters appearing in this episode: {chars_str}."
        
        documents.append(text_chunk)
        ids.append(f"episode_{ep_id}")
        metadatas.append({
            "id": int(ep_id),
            "entity_type": "episode",
            "name": ep["name"],
            "type_or_species": ep["episode"]
        })

    # 4. Process CHARACTERS
    print("Processing Characters...")
    for char_id, char in characters.items():
        # Resolve where they come from and where they are now
        origin_name = char["origin"]["name"]
        current_loc_name = char["location"]["name"]
        
        # Resolve what episodes they appeared in
        ep_codes = [
            episodes[ep_idx]["episode"] 
            for url in char["episode"] 
            if (ep_idx := extract_id(url)) in episodes
        ]
        episodes_str = ", ".join(ep_codes) if ep_codes else "none"
        
        text_chunk = (
            f"Character: {char['name']}. Status: {char['status']}. Species: {char['species']}. "
            f"Gender: {char['gender']}. Origin: {origin_name}. Current Location: {current_loc_name}. "
            f"Appeared in episodes: {episodes_str}."
        )
        
        documents.append(text_chunk)
        ids.append(f"character_{char_id}")
        metadatas.append({
            "id": int(char_id),
            "entity_type": "character",
            "name": char["name"],
            "type_or_species": char["species"]
        })

    # 5. Initialize Local VectorDB & Embeddings (ChromaDB)
    print("\nInitializing local Vector Database...")
    client = chromadb.PersistentClient(path="./rm_vectordb")
    
    # Define local embedding function ( all-MiniLM-L6-v2)
    local_embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Create or fetch collection
    collection = client.get_or_create_collection(
        name="rick_and_morty_rag",
        embedding_function=local_embedding_model
    )
    
    # Upsert data
    print(f"Uploading {len(documents)} unified documents into VectorDB...")
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    print("Vector Database build complete successfully!")

if __name__ == "__main__":
    generate_and_load_rag_docs()