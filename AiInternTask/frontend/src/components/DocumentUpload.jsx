import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { documentApi } from '../services/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

const DocumentUpload = () => {
  const [title, setTitle] = useState('');
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');
  const queryClient = useQueryClient();

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (file) {
        // Extract title from filename (remove extension)
        const fileName = file.name;
        const fileNameWithoutExt = fileName.split('.').slice(0, -1).join('.');
        setTitle(fileNameWithoutExt);

        setFiles(acceptedFiles.map(file => Object.assign(file, {
          preview: URL.createObjectURL(file)
        })));
      }
      setError('');
    },
    onDropRejected: () => {
      setError('Please upload a valid PDF or image file.');
    }
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, title }) => documentApi.uploadDocument(file, title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setFiles([]);
      setTitle('');
    },
    onError: (error) => {
      setError(`Upload failed: ${error.message}`);
    }
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (files.length === 0) {
      setError('Please upload a file.');
      return;
    }

    uploadMutation.mutate({ file: files[0], title });
  };

  return (
    <Paper elevation={2} className="upload-paper-custom" sx={{ p: 2, mb: 2 }}>
      <Typography variant="h5" gutterBottom>
        Upload Document
      </Typography>

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Document Title"
          variant="outlined"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={uploadMutation.isPending}
          sx={{ mb: 2 }}
        />

        <Box
          {...getRootProps()}
          sx={{
            cursor: 'pointer',
            mb: 2,
            border: '2px dashed #cccccc',
            borderRadius: 2,
            p: 3,
            mt: 2,
            textAlign: 'center',
            '&:hover': {
              borderColor: 'primary.main',
            }
          }}
        >
          <input {...getInputProps()} />
          <CloudUploadIcon color="primary" sx={{ fontSize: 40 }} />
          <Typography variant="subtitle1" color="primary">
            Drag & drop a PDF or image file here, or click to select
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Supported formats: PDF, JPG, PNG, TIFF
          </Typography>
        </Box>

        {files.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2">
              Selected file: {files[0].name} ({(files[0].size / 1024 / 1024).toFixed(2)} MB)
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          disabled={uploadMutation.isPending || files.length === 0}
          sx={{ mt: 2 }}
        >
          {uploadMutation.isPending ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1 }} color="inherit" />
              Uploading...
            </>
          ) : (
            'Upload Document'
          )}
        </Button>
      </form>
    </Paper>
  );
};

export default DocumentUpload;
