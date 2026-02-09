import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://farm-ai-assistant.onrender.com/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add basic auth to requests (except for auth endpoints)
api.interceptors.request.use(
  (config) => {
    // Don't add auth for login/register endpoints
    if (!config.url.includes('/auth/login') && !config.url.includes('/auth/register')) {
      const credentials = localStorage.getItem('credentials');
      if (credentials) {
        config.auth = {
          username: credentials.split(':')[0],
          password: credentials.split(':')[1],
        };
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
};

// Chat API calls
export const chatAPI = {
  sendMessage: (data) => api.post('/chat/', data),
  getChatHistory: () => api.get('/chat/history'),
};

// Season API calls
export const seasonAPI = {
  createSeason: (data) => api.post('/seasons/', data),
  getSeasons: () => api.get('/seasons/'),
  getCurrentSeason: () => api.get('/crop/current-season'),
};

export default api;
