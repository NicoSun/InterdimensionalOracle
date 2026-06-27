# 🌀 InterdimensionalOracle
A Rick&amp;Morty Oracle answering questions about the show using knowledge from rickandmortyapi

---

## 📖 Table of Contents (H2)
* [About the Project](#about-the-project)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [License](#license)

## 🧐 About the Project
- create a local cache of https://rickandmortyapi.com/api/
- use it to experiment with different database designs


## ✨ Features
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
  python app.py
  ```

terminal2
  ```bash
  cd frontend
  npm run dev
  ```
