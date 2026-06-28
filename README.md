# 🌀 InterdimensionalOracle
A Rick&amp;Morty Oracle answering questions about the show using knowledge from rickandmortyapi (https://rickandmortyapi.com/api/)

---

## 📖 Table of Contents (H2)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [License](#license)


## ✨ Features
creates a local cache of the api knowledge which can be used to experiment with different database designs

supports local LLM (ollama), OpenAI & Gemini for response generation

> Note: OpenAI wasn't tested because I don't have API credits



## 🛠 Tech Stack
| Technology | Purpose |
| :--- | :--- |
| Vue.js | Frontend Library |
| Python| Backend API |
| FastAPI | Websocket | 
| ChromaDB | Database | 
| SentenceTransformer | Embeddings |

### Tech stack justifications
Websocket allows token streaming which great for slow LLM responses. A simple API would wait until the whole message is generated.
ChromaDB & SentenceTransformer are simple local vector databse and RAG retrieval technologies.
They can easily be exchanged. With more time I would prioretise optimizing the database generation and retrieval.


## 💻 Install Guide

### Prerequisites
npm & python

### Installation
  ```bash
  python setup.py
  ```
installs python venv and vue (npm)
it also downloads data from the API to create a vector database

## 💻 Usage (H2)

terminal1
```bash
  cd backend
  source venv/bin/activate
  python app.py
  ```

terminal2
  ```bash
  cd frontend
  npm run dev
  ```
