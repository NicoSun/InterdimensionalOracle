import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue';

export function useOracleChat() {
  const messages = ref([]);
  const inputQuery = ref('');
  const activeResponse = ref('');
  const activeSources = ref([]);
  const isStreaming = ref(false);
  const historyRef = ref(null);

  const config = reactive({
    provider: 'local',
    apiKey: ''
  });

  const ws = ref(null);
  const wsStatus = ref('disconnected');

  const wsStatusText = computed(() => {
    switch (wsStatus.value) {
      case 'connected': return 'Database Synced';
      case 'connecting': return 'Syncing...';
      default: return 'No Database Connection';
    }
  });

  const scrollToBottom = () => {
    nextTick(() => {
      if (historyRef.value) {
        historyRef.value.scrollTop = historyRef.value.scrollHeight;
      }
    });
  };

  const resetStreamState = () => {
    isStreaming.value = false;
    activeResponse.value = '';
    activeSources.value = [];
  };

  const connectWebSocket = () => {
    wsStatus.value = 'connecting';
    ws.value = new WebSocket('ws://localhost:8000/ws');

    ws.value.onopen = () => {
      wsStatus.value = 'connected';
    };

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'sources') {
        activeSources.value = data.sources;
      } else if (data.type === 'token') {
        activeResponse.value += data.text;
      } else if (data.type === 'error') {
        messages.value.push({
          sender: 'oracle',
          text: data.message,
          sources: []
        });
        resetStreamState();
      } else if (data.type === 'done') {
        if (activeResponse.value) {
          messages.value.push({
            sender: 'oracle',
            text: activeResponse.value,
            sources: [...activeSources.value]
          });
        }
        resetStreamState();
      }
      scrollToBottom();
    };

    ws.value.onclose = () => {
      wsStatus.value = 'disconnected';
      // Reconnection loop every 5 seconds if disconnected
      setTimeout(connectWebSocket, 5000);
    };
  };

  const sendQuery = () => {
    if (isStreaming.value || !inputQuery.value.trim()) return;
    if (wsStatus.value !== 'connected') {
      alert("Connection lost. Trying to reconnect to Python backend...");
      return;
    }

    const userQuery = inputQuery.value;
    messages.value.push({ sender: 'user', text: userQuery });
    
    isStreaming.value = true;
    activeResponse.value = '';
    activeSources.value = [];
    inputQuery.value = '';

    ws.value.send(JSON.stringify({
      query: userQuery,
      provider: config.provider,
      api_key: config.apiKey
    }));

    scrollToBottom();
  };

  onMounted(() => {
    connectWebSocket();
  });

  onUnmounted(() => {
    if (ws.value) ws.value.close();
  });

  // Expose everything the component needs to know/do
  return {
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
  };
}
