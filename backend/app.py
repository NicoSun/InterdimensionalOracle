#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 17:15:53 2026

@author: nico
"""
import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from chromadb.utils import embedding_functions
import httpx
from query_db import search_rag

# LLM Providers SDKs
from openai import AsyncOpenAI
import google.genai as genai

openAI_model = "gpt-5.4-nano"
gemini_model = "gemini-3.5-flash"


app = FastAPI(title="Rick & Morty Oracle Backend")

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#response settings
GUARDRAIL_THRESHOLD = 0.75  # Cosine distance limit (lower is closer; adjust based on testing)
SYSTEM_PROMPT_TEMPLATE = """You are the Interdimensional Oracle, you speak in the style of a generic Rick from the Council of Ricks.
Your goal is to answer the user's questions about characters, locations, and events.

Strict Operational Guidelines:
1. Only answer questions about Rick&Morty characters, locations & episodes. Don't write code, poems, stories, etc 
2. You MUST answer the user's question using ONLY the retrieved Context Documents provided below, no outside knowledge
3. If the Context Documents do not contain enough information to answer the question, you MUST reply with: "Sorry, I don't know pal. Ask about something else."
4. Keep your responses informative but laced with slight, mild universe-appropriate attitude.
5. Do not mention "provided context", "documents", or "according to the database" in your response. Answer as if you naturally hold this knowledge.

Context Documents:
{context}
"""

async def stream_openai(prompt: str, api_key: str, websocket: WebSocket):
    client = AsyncOpenAI(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model=openAI_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        async for chunk in response:
            token = chunk.choices[0].delta.content
            if token:
                await websocket.send_json({"type": "token", "text": token})
    except Exception as e:
        await websocket.send_json({"type": "error", "message": f"OpenAI Error: {str(e)}"})

async def stream_gemini(prompt: str, api_key: str, websocket: WebSocket):
    try:

        client = genai.Client(api_key=api_key)
        response_stream = await client.aio.models.generate_content_stream(
            model=gemini_model,
            contents=prompt
        )

        async for chunk in response_stream:
            if chunk.text:
                await websocket.send_json({"type": "token", "text": chunk.text})
                # Add a tiny yield to let event loop breathe
                await asyncio.sleep(0.01)

    except Exception as e:
        await websocket.send_json({"type": "error", "message": f"Gemini Error: {str(e)}"})


async def stream_local(prompt: str, api_key: str, websocket: WebSocket):
    """Streams from a local Ollama instance (default port 11434)."""
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": api_key,  # 
        "prompt": prompt,
        "stream": True
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", ollama_url, json=payload) as response:
                if response.status_code != 200:
                    await websocket.send_json({"type": "error", "message": f"Local LLM Error (HTTP {response.status_code})"})
                    return

                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            await websocket.send_json({"type": "token", "text": token})
    except Exception as e:
        await websocket.send_json({"type": "error", "message": f"Local LLM connection failed: {str(e)}. Make sure Ollama is running."})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected via WebSocket.")

    try:
        while True:
            # 1. Receive incoming query payload
            data = await websocket.receive_text()
            payload = json.loads(data)

            query = payload.get("query", "").strip()
            provider = payload.get("provider", "local").lower()
            api_key = payload.get("api_key", "").strip()

            if not query:
                await websocket.send_json({"type": "error", "message": "Query cannot be empty."})
                continue

            # 2. RAG Pipeline: Retrieve knowledge from Vector DB
            documents, metadatas = search_rag(query_text=query,max_distance=GUARDRAIL_THRESHOLD)

            # Code-Level Guardrail Triggered (No matching records found within threshold)
            if not documents:
                await websocket.send_json({
                    "type": "error",
                    "message": "This query doesn't match my database. Keep it to Rick and Morty topics, pal."
                })
                await websocket.send_json({"type": "done"})
                continue

            # 3. Emit sources back to frontend before streaming LLM response
            sources = [{"type": m.get("type_or_species"), "name": m.get("name"), "id": m.get("id"),"distance":m.get("distance")} for m in metadatas]
            await websocket.send_json({"type": "sources", "sources": sources})

            # 4. Construct Prompt
            context_str = "\n\n".join(documents)
            formatted_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_str) + f"\nUser Query: {query}\nOracle Response:"

            # 5. Route to selected provider
            if provider == "openai":
                if not api_key:
                    await websocket.send_json({"type": "error", "message": "Missing OpenAI API key."})
                else:
                    await stream_openai(formatted_prompt, api_key, websocket)
            elif provider == "gemini":
                if not api_key:
                    await websocket.send_json({"type": "error", "message": "Missing Gemini API key."})
                else:
                    await stream_gemini(formatted_prompt, api_key, websocket)
            elif provider == "local":
                await stream_local(formatted_prompt, api_key, websocket)
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown provider: {provider}"})

            # Signal completion of the stream
            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Server error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": "An internal server error occurred."})
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn
    # Start the server on port 8000
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
