#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 15:02:42 2026

@author: nico
"""

import json
import requests

def build_local_cache():
    master_cache = {
        "characters": {},
        "locations": {},
        "episodes": {}
    }
    
    endpoints = ["character", "location", "episode"]
    
    for endpoint in endpoints:
        print(f"Downloading {endpoint} data from API...")
        
        # Step 1: Query the endpoint base to check the total item count
        base_response = requests.get(f"https://rickandmortyapi.com/api/{endpoint}").json()
        total_items = base_response['info']['count']
        
        # Step 2: Use the bulk ID URL syntax: /api/{endpoint}/1,2,3...N
        all_ids = ",".join(str(i) for i in range(1, total_items + 1))
        bulk_url = f"https://rickandmortyapi.com/api/{endpoint}/{all_ids}"
        
        bulk_data = requests.get(bulk_url).json()
        
        # Enforce list formatting just in case an endpoint returns a single dictionary
        if isinstance(bulk_data, dict):
            bulk_data = [bulk_data]
            
        # Step 3: Populate our local schema dict utilizing string IDs for stable JSON keys
        plural_key = f"{endpoint}s"
        for item in bulk_data:
            master_cache[plural_key][str(item['id'])] = item

    filename = "db_json/rick_and_morty_raw_cache.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(master_cache, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccess! Total items cached:")
    for key, data in master_cache.items():
        print(f" - {key}: {len(data)} entries")

if __name__ == "__main__":
    build_local_cache()