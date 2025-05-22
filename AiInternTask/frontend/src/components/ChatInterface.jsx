import { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  LinearProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { useMutation, useQuery } from '@tanstack/react-query';
import { queryApi, healthApi } from '../services/api';
import ResponseDisplay from './ResponseDisplay';

const ChatInterface = () => {
  const [query, setQuery] = useState('');
  const [currentResponse, setCurrentResponse] = useState(null);
  const [error, setError] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime, setStartTime] = useState(null);

  // Check if Ollama is available
  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: healthApi.checkHealth,
    refetchInterval: 30000,
    staleTime: 10000,
  });

  const isOllamaAvailable = healthData?.ollama === 'available';

  // Define queryMutation first
  const queryMutation = useMutation({
    mutationFn: (queryText) => queryApi.createQuery(queryText),
    onMutate: () => {
      setStartTime(Date.now());
      setElapsedTime(0);
    },
    onSuccess: (data) => {
      const queryTime = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`Query completed in ${queryTime} seconds`);
      setCurrentResponse(data);
      setQuery('');
      setStartTime(null);
    },
    onError: (error) => {
      setStartTime(null);
      // Provide more helpful error messages
      if (error.message.includes('timeout')) {
        setError('Query timed out. The server is taking too long to respond. Try a simpler query or try again later.');
      } else if (error.message.includes('Network Error')) {
        setError('Network error. Please check your connection and make sure the backend server is running.');
      } else {
        setError(`Query failed: ${error.message}`);
      }
    }
  });

  // Effect to track elapsed time during query processing
  useEffect(() => {
    let timer;
    if (queryMutation.isPending && startTime) {
      timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        setElapsedTime(elapsed);
      }, 1000);
    } else {
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [queryMutation.isPending, startTime]);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a query.');
      return;
    }

    setError('');
    queryMutation.mutate(query);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
      <Paper elevation={3} className="chat-paper-custom" sx={{ p: 3, mb: 3, flexGrow: 1, overflow: 'auto', minHeight: '300px' }}>
        <Typography variant="h5" gutterBottom color="primary">
          Research Assistant
        </Typography>

        {!currentResponse && !queryMutation.isPending && (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="body1" color="textSecondary">
              Ask a question to search across your documents.
            </Typography>
          </Box>
        )}

        {queryMutation.isPending && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 3 }}>
            <CircularProgress />
            <Typography variant="body1" sx={{ mt: 2 }}>
              Analyzing documents... {elapsedTime > 0 ? `(${elapsedTime}s)` : ''}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {elapsedTime < 5 ?
                "Processing your query..." :
                elapsedTime < 15 ?
                  "This may take up to a minute." :
                  "Still working... Complex queries can take longer to process."
              }
            </Typography>
            {elapsedTime > 20 && (
              <Box sx={{ width: '100%', mt: 2 }}>
                <LinearProgress variant="indeterminate" color="secondary" />
              </Box>
            )}
          </Box>
        )}

        {!isOllamaAvailable && !queryMutation.isPending && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Ollama is not running.</strong> Queries will be slower and less accurate.
            </Typography>
          </Alert>
        )}

        {currentResponse && (
          <ResponseDisplay response={currentResponse} />
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 2 }}>
        <form onSubmit={handleSubmit}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask a question..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={queryMutation.isPending}
              sx={{ mr: 2 }}
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              endIcon={<SendIcon />}
              disabled={queryMutation.isPending}
            >
              Send
            </Button>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
