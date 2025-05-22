import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { healthApi } from '../services/api';

const ConnectionStatus = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.checkHealth,
    refetchInterval: 30000,
    retry: 3,
    retryDelay: 1000,
    staleTime: 10000,
  });

  useEffect(() => {
    if (isLoading) {
      console.log('Checking connection status...');
    } else if (error) {
      console.error('Connection error:', error);
    } else if (data) {
      console.log('Connection Status:', {
        MongoDB: data.mongodb,
        Ollama: data.ollama,
        ChromaDB: data.chromadb || 'unknown',
        Status: data.status || 'unknown'
      });
    }
  }, [data, isLoading, error]);

  return null;
};

export default ConnectionStatus;
