import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query';
import App from './App.vue';
import './assets/styles/main.css';

// Create Vue application
const app = createApp(App);

// Create Pinia store
const pinia = createPinia();
app.use(pinia);

// Create TanStack Query client with default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: how long data is considered fresh
      staleTime: 1000 * 60 * 5, // 5 minutes
      // Cache time: how long inactive data stays in cache
      gcTime: 1000 * 60 * 30, // 30 minutes
      // Retry failed queries
      retry: 1,
      // Refetch on window focus (useful for real-time data)
      refetchOnWindowFocus: false,
    },
    mutations: {
      // Retry failed mutations
      retry: 0,
    },
  },
});

app.use(VueQueryPlugin, { queryClient });

// Initialize theme from localStorage or system preference
const initializeTheme = () => {
  const savedTheme = localStorage.getItem('kometa-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme === 'light') {
    document.documentElement.classList.add('light');
  } else if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.remove('light');
  } else {
    // System preference
    if (!prefersDark) {
      document.documentElement.classList.add('light');
    }
  }
};

initializeTheme();

// Mount the application
app.mount('#app');
