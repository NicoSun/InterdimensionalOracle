<template>
  <div class="oracle-app">
    <!-- Header -->
    <header class="app-header">
      <div class="brand">
        <span class="portal-effect">🌀</span>
        <h1>Rick & Morty Oracle</h1>
      </div>
      <div class="connection-status" :class="wsStatus">
        {{ wsStatusText }}
      </div>
    </header>

    <div class="main-layout">
      <!-- Config Sidebar -->
      <aside class="sidebar">
        <h2>Configuration</h2>
        <div class="form-group">
          <label>LLM Provider</label>
          <select v-model="config.provider">
            <option value="local">Local (Ollama)</option>
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
          </select>
        </div>

        <div v-if="config.provider == 'local'" class="form-group">
          <label>local model name</label>
          <input 
            type="text" 
            v-model="config.apiKey" 
            placeholder="Enter the model name.."
          />
        </div>

        <div v-if="config.provider !== 'local'" class="form-group">
          <label>API Key</label>
          <input 
            type="password" 
            v-model="config.apiKey" 
            placeholder="Enter your API key..."
          />
        </div>

        <div class="notes">
          <p v-if="config.provider === 'local'">
            Ensure Ollama is running locally on port 11434 with your selected model.
          </p>
          <p v-else>
            Your API key is only processed locally in-memory and sent via WebSockets to complete your query.
          </p>
        </div>
      </aside>

      <!-- Chat Engine -->
      <main class="chat-container">
        <div class="message-history" ref="historyRef">
          <div v-if="messages.length === 0" class="welcome-screen">
            <div class="oracle-avatar">🔮</div>
            <h3>Ask the Omniscient Oracle</h3>
            <p>Inquire about any character, dimension, or episode within the multiverse. Answers are validated strictly against the central database.</p>
          </div>

          <div 
            v-for="(msg, idx) in messages" 
            :key="idx" 
            class="message-bubble" 
            :class="msg.sender"
          >
            <div class="message-meta">
              {{ msg.sender === 'user' ? 'You' : 'Oracle' }}
            </div>
            <div class="message-content">
              <p>{{ msg.text }}</p>
            </div>
            
            <!-- Sources Display -->
            <div v-if="msg.sources && msg.sources.length > 0" class="sources-panel">
              <span class="sources-title">Verified Dimensions/Entities:</span>
              <div class="source-tags">
                <span 
                  v-for="(source, sIdx) in msg.sources" 
                  :key="sIdx" 
                  class="source-tag"
                  :class="source.type"
                >
                  [{{ source.type }}] {{ source.name }}
                  <span class="confidence-text">
                    ({{ distanceConfidence(source.distance).label }})
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- Active Streaming Target -->
          <div v-if="activeResponse" class="message-bubble oracle streaming">
            <div class="message-meta">Oracle</div>
            <div class="message-content">
              <p>{{ activeResponse }}</p>
            </div>
            <div v-if="activeSources.length > 0" class="sources-panel">
              <span class="sources-title">Verified Dimensions/Entities:</span>
              <div class="source-tags">
                <span v-for="(source, sIdx) in activeSources" :key="sIdx" class="source-tag" :class="source.type">
                  [{{ source.type }}] {{ source.name }}
                  <span class="confidence-text">
                    ({{ distanceConfidence(source.distance).label }})
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Controls -->
        <form @submit.prevent="sendQuery" class="chat-input-form">
          <input 
            v-model="inputQuery" 
            type="text" 
            placeholder="Where is Earth C-137? / Who is Birdperson?" 
            :disabled="isStreaming"
          />
          <button type="submit" :disabled="isStreaming || !inputQuery.trim()">
            {{ isStreaming ? 'Computing...' : 'Ask Oracle' }}
          </button>
        </form>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useOracleChat, distanceConfidence } from './composables/useOracleChat';

const { 
  messages, 
  inputQuery, 
  activeResponse, 
  activeSources, 
  isStreaming, 
  historyRef, 
  config, 
  wsStatus, 
  wsStatusText, 
  sendQuery 
} = useOracleChat();
</script>