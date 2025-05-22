# Document Research Chatbot Frontend

This is the frontend for the Document Research Chatbot, built with React, Material-UI, and React Query.

## Features

- Document upload interface
- Document management
- Chat interface for queries
- Response display with citations and themes

## Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

The application will be available at http://localhost:5173.

## Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Project Structure

- `src/components/` - React components
  - `DocumentUpload.jsx` - Document upload component
  - `DocumentList.jsx` - Document listing component
  - `ChatInterface.jsx` - Chat interface component
  - `ResponseDisplay.jsx` - Response display component
  - `ConnectionStatus.jsx` - Backend connection status component
- `src/services/` - API services
  - `api.js` - API client for backend communication
- `src/App.jsx` - Main application component
- `src/main.jsx` - Application entry point

## Configuration

The frontend is configured to connect to the backend at `http://localhost:8000`. If you need to change this, update the `API_PORT` variable in `src/services/api.js`.
