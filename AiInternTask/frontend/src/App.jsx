import {
  CssBaseline,
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Grid,
  ThemeProvider,
  createTheme,
  Stack
} from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import ConnectionStatus from './components/ConnectionStatus';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
      light: '#e8eaf6',
    },
    secondary: {
      main: '#f50057',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  // No longer tracking selected document as we're using all documents by default

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        {/* Include ConnectionStatus for console logging but don't show in UI */}
        <ConnectionStatus />

        <AppBar position="static" color="primary" elevation={0}>
          <Toolbar>
            <Stack direction="row" alignItems="center" spacing={1}>
              <AutoAwesomeIcon />
              <Typography variant="h6" component="div">
                Document Research Chatbot
              </Typography>
            </Stack>
            <Box sx={{ flexGrow: 1 }} />
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Grid container spacing={3}>
            {/* Left Column - Document Management */}
            <Grid item xs={12} md={4}>
              <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                height: 'calc(100vh - 180px)',
                overflow: 'hidden'
              }}>
                <DocumentUpload />
                <Box sx={{ flexGrow: 1, overflow: 'auto', mt: 2 }}>
                  <DocumentList />
                </Box>
              </Box>
            </Grid>

            {/* Right Column - Chat Interface */}
            <Grid item xs={12} md={8}>
              <Box sx={{
                height: 'calc(100vh - 180px)',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden'
              }}>
                <ChatInterface />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
