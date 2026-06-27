# InterdimensionalOracle
A Rick&amp;Morty Oracle answering questions about the show using knowledge from rickandmortyapi


- create a local cache of https://rickandmortyapi.com/api/
- use it to experiment with different database designs


# Webapp Design
Backend: Use FastAPI with WebSockets
Frontend: Vue.js with native WebSocket
Message flow: Vue.js emits message → Python backend retrieves from Vector-DB → streams response back in real-time

