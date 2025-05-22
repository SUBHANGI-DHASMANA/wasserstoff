import React from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  CircularProgress,
  Skeleton,
  Button
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import ImageIcon from '@mui/icons-material/Image';
import { useQuery } from '@tanstack/react-query';
import { documentApi } from '../services/api';

const DocumentList = () => {
  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: documentApi.getAllDocuments
  });

  const getFileIcon = (fileType) => {
    if (fileType === 'pdf') {
      return <DescriptionIcon />;
    } else if (['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp'].includes(fileType)) {
      return <ImageIcon />;
    }
    return <DescriptionIcon />;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) {
      return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    } else {
      return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (isLoading) {
    return (
      <Paper elevation={2} className="document-list-custom" sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" color="primary">
            Uploaded Documents
          </Typography>
          <Skeleton variant="rounded" width={80} height={24} />
        </Box>

        {/* Loading skeleton */}
        {[1, 2, 3].map((item) => (
          <React.Fragment key={item}>
            <Box sx={{ display: 'flex', p: 1, my: 1 }}>
              <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
              <Box sx={{ width: '100%' }}>
                <Skeleton variant="text" width="60%" height={24} />
                <Skeleton variant="text" width="40%" height={20} />
                <Box sx={{ display: 'flex', mt: 1 }}>
                  <Skeleton variant="rounded" width={60} height={24} sx={{ mr: 1 }} />
                  <Skeleton variant="rounded" width={100} height={24} />
                </Box>
              </Box>
            </Box>
            <Divider />
          </React.Fragment>
        ))}
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper elevation={2} className="document-list-custom" sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" color="primary" gutterBottom>
          Uploaded Documents
        </Typography>
        <Box sx={{ p: 2, bgcolor: 'error.light', borderRadius: 1 }}>
          <Typography color="error.dark" gutterBottom>
            Error loading documents
          </Typography>
          <Typography variant="body2" color="error.dark">
            {error.message.includes('Network Error')
              ? 'Cannot connect to the server. Please check if the backend is running.'
              : `Error: ${error.message}`}
          </Typography>
          <Button
            variant="outlined"
            color="error"
            size="small"
            sx={{ mt: 1 }}
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} className="document-list-custom" sx={{ p: 2, mb: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6" color="primary">
          Uploaded Documents
        </Typography>
        {documents?.length > 0 && (
          <Chip
            label={`${documents.length} ${documents.length === 1 ? 'document' : 'documents'}`}
            size="small"
            color="primary"
            variant="outlined"
          />
        )}
      </Box>

      {documents?.length === 0 ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexGrow: 1 }}>
          <Typography variant="body1" color="textSecondary" sx={{ p: 2 }}>
            No documents uploaded yet. Upload a document to get started.
          </Typography>
        </Box>
      ) : (
        <List sx={{ flexGrow: 1, overflow: 'auto', maxHeight: 'calc(100vh - 300px)' }}>
          {documents?.map((document) => (
            <React.Fragment key={document.id}>
              <ListItem
                sx={{
                  borderRadius: 1,
                  p: 2
                }}
              >
                <ListItemIcon>
                  {getFileIcon(document.file_type)}
                </ListItemIcon>
                <ListItemText
                  primary={document.title}
                  secondary={
                    <React.Fragment>
                      <Typography variant="body2" component="span">
                        {document.original_filename} • {formatFileSize(document.file_size)}
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip
                          size="small"
                          label={`${document.page_count} pages`}
                          sx={{ mr: 1, mb: 1 }}
                        />
                        {document.ocr_processed && (
                          <Chip
                            size="small"
                            label="OCR Processed"
                            color="secondary"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        )}
                        <Chip
                          size="small"
                          label={`Uploaded: ${formatDate(document.upload_date)}`}
                          variant="outlined"
                          sx={{ mb: 1 }}
                        />
                      </Box>
                    </React.Fragment>
                  }
                />
              </ListItem>
              <Divider component="li" />
            </React.Fragment>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default DocumentList;
