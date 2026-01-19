import { ref, onMounted, onUnmounted, watch } from 'vue';
import type { Ref } from 'vue';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (data: unknown) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

interface UseWebSocketReturn {
  connected: Ref<boolean>;
  connecting: Ref<boolean>;
  error: Ref<Event | null>;
  data: Ref<unknown>;
  send: (message: unknown) => void;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(
  endpoint: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    autoConnect = true,
    reconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    onMessage,
    onOpen,
    onClose,
    onError,
  } = options;

  const socket = ref<WebSocket | null>(null);
  const connected = ref(false);
  const connecting = ref(false);
  const error = ref<Event | null>(null);
  const data = ref<unknown>(null);
  const reconnectAttempts = ref(0);
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  const getWebSocketUrl = (): string => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}${endpoint}`;
  };

  const connect = () => {
    if (socket.value?.readyState === WebSocket.OPEN) {
      return;
    }

    connecting.value = true;
    error.value = null;

    try {
      socket.value = new WebSocket(getWebSocketUrl());

      socket.value.onopen = () => {
        connected.value = true;
        connecting.value = false;
        reconnectAttempts.value = 0;
        onOpen?.();
      };

      socket.value.onmessage = (event: MessageEvent) => {
        try {
          const parsed = JSON.parse(event.data);
          data.value = parsed;
          onMessage?.(parsed);
        } catch {
          // If not JSON, use raw data
          data.value = event.data;
          onMessage?.(event.data);
        }
      };

      socket.value.onclose = () => {
        connected.value = false;
        connecting.value = false;
        onClose?.();

        // Attempt to reconnect
        if (reconnect && reconnectAttempts.value < maxReconnectAttempts) {
          reconnectAttempts.value++;
          reconnectTimer = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      socket.value.onerror = (event: Event) => {
        error.value = event;
        connecting.value = false;
        onError?.(event);
      };
    } catch (err) {
      connecting.value = false;
      console.error('WebSocket connection error:', err);
    }
  };

  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    if (socket.value) {
      socket.value.close();
      socket.value = null;
    }

    connected.value = false;
    connecting.value = false;
  };

  const send = (message: unknown) => {
    if (socket.value?.readyState === WebSocket.OPEN) {
      const payload = typeof message === 'string' ? message : JSON.stringify(message);
      socket.value.send(payload);
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  };

  onMounted(() => {
    if (autoConnect) {
      connect();
    }
  });

  onUnmounted(() => {
    disconnect();
  });

  return {
    connected,
    connecting,
    error,
    data,
    send,
    connect,
    disconnect,
  };
}

/**
 * Specialized WebSocket for log streaming
 */
export function useLogWebSocket() {
  return useWebSocket('/ws/logs', {
    autoConnect: true,
    reconnect: true,
    reconnectInterval: 2000,
  });
}

/**
 * Specialized WebSocket for run status updates
 */
export function useStatusWebSocket() {
  return useWebSocket('/ws/status', {
    autoConnect: true,
    reconnect: true,
    reconnectInterval: 2000,
  });
}
