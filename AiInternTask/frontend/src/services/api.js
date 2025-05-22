import axios from 'axios';

const API_PORT = 8000;

const api = axios.create({
  baseURL: `http://localhost:${API_PORT}/api`,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 60000,
  withCredentials: false,
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.data && error.response.data.detail) {
      if (error.response.data.detail.includes('MongoDB')) {
        console.error('MongoDB Atlas connection error:', error.response.data.detail);
      }
    }
    return Promise.reject(error);
  }
);

export const healthApi = {
  checkHealth: async () => {
    try {
      const response = await axios.get(`http://localhost:${API_PORT}/health`, {
        timeout: 5000,
        headers: {
          'Accept': 'application/json',
        }
      });
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return {
        mongodb: 'disconnected',
        ollama: 'unavailable',
        chromadb: 'disconnected',
        status: 'error'
      };
    }
  },
};

export const documentApi = {
  uploadDocument: async (file, title = null) => {
    const formData = new FormData();
    formData.append('file', file);

    if (title) {
      formData.append('title', title);
    }

    const response = await api.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  getAllDocuments: async () => {
    const response = await api.get('/documents');
    return response.data;
  },

  getDocument: async (documentId) => {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },
};

export const queryApi = {
  createQuery: async (queryText) => {
    const response = await api.post('/queries', {
      text: queryText,
    });

    return response.data;
  },

  getQuery: async (queryId) => {
    const response = await api.get(`/queries/${queryId}`);
    return response.data;
  },
};

export default api;
