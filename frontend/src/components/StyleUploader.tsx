import React, { useState, useCallback } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Chip,
  Stack,
  Alert,
  Snackbar,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon, AutoFixHigh as PresetIcon, Download as DownloadIcon } from '@mui/icons-material';
import axios, { AxiosError } from 'axios';
import ResultScreen from './ResultScreen';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface StyleUploaderProps {}

interface PresetResult {
  preset_id: string;
  style_description: string;
  xmp_url: string;
  preview_url: string;
}

interface ErrorResponse {
  detail: string;
}

interface ErrorState {
  message: string;
  details?: string;
}

const EXAMPLE_PROMPTS = [
  'Cinematic moody look',
  'Vintage film grain',
  'High contrast dramatic',
  'Soft dreamy aesthetic',
  'Film noir style',
];

const StyleUploader: React.FC<StyleUploaderProps> = () => {
  const [file, setFile] = useState<File | null>(null);
  const [styleDescription, setStyleDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<PresetResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showSnackbar, setShowSnackbar] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      if (!selectedFile.type.startsWith('image/')) {
        setError({
          message: 'Invalid file type',
          details: 'Please upload an image file (JPG, PNG, or GIF)'
        });
        return;
      }
      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError({
          message: 'File too large',
          details: 'Please upload an image smaller than 10MB'
        });
        return;
      }
      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      if (!droppedFile.type.startsWith('image/')) {
        setError({
          message: 'Invalid file type',
          details: 'Please upload an image file (JPG, PNG, or GIF)'
        });
        return;
      }
      if (droppedFile.size > 10 * 1024 * 1024) {
        setError({
          message: 'File too large',
          details: 'Please upload an image smaller than 10MB'
        });
        return;
      }
      setFile(droppedFile);
      setError(null);
      setResult(null);
    }
  }, []);

  const handleSubmit = async () => {
    if (!file) {
      setError({
        message: 'No file selected',
        details: 'Please select an image to process'
      });
      return;
    }

    if (!styleDescription.trim()) {
      setError({
        message: 'No style description',
        details: 'Please enter a style description or select a preset'
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('style_description', styleDescription);

    try {
      setUploading(true);
      setError(null);
      setIsProcessing(true);
      
      const response = await axios.post<PresetResult>(`${API_URL}/generate_preset/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      setShowSnackbar(true);
      
      // Don't reset form immediately
      setStyleDescription('');
    } catch (error) {
      const axiosError = error as AxiosError<ErrorResponse>;
      setError({
        message: 'Failed to generate preset',
        details: axiosError.response?.data?.detail || 'Please try again'
      });
    } finally {
      setUploading(false);
      setIsProcessing(false);
    }
  };

  const handlePresetClick = (prompt: string) => {
    setStyleDescription(prompt);
    setError(null);
  };

  const generatePreset = () => {
    const randomPrompt = EXAMPLE_PROMPTS[Math.floor(Math.random() * EXAMPLE_PROMPTS.length)];
    setStyleDescription(randomPrompt);
    setError(null);
  };

  const handleDownloadXMP = async () => {
    if (!result) return;
    
    try {
      const response = await axios.get(`${API_URL}${result.xmp_url}`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `preset_${result.preset_id}.xmp`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setShowSnackbar(true);
    } catch (error) {
      setError({
        message: 'Download failed',
        details: 'Failed to download XMP file. Please try again.'
      });
    }
  };

  const handleDownloadEdited = async () => {
    if (!result) return;
    
    try {
      const response = await axios.get(`${API_URL}${result.preview_url}`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `edited_${result.preset_id}.jpg`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setShowSnackbar(true);
    } catch (error) {
      setError({
        message: 'Download failed',
        details: 'Failed to download edited image. Please try again.'
      });
    }
  };

  const handleCloseSnackbar = () => {
    setShowSnackbar(false);
  };

  const handleStartOver = () => {
    setFile(null);
    setResult(null);
    setStyleDescription('');
    setError(null);
  };

  return (
    <>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Upload your image
        </Typography>

        <Box
          sx={{
            mb: 3,
            p: 3,
            border: '2px dashed',
            borderColor: isDragging ? 'primary.main' : 'grey.300',
            borderRadius: 1,
            backgroundColor: isDragging ? 'action.hover' : 'background.paper',
            transition: 'all 0.2s ease',
            cursor: 'pointer',
            opacity: uploading ? 0.7 : 1,
            pointerEvents: uploading ? 'none' : 'auto',
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('style-file-upload')?.click()}
        >
          <input
            type="file"
            id="style-file-upload"
            style={{ display: 'none' }}
            onChange={handleFileChange}
            accept="image/*"
            disabled={uploading}
          />
          <Box sx={{ textAlign: 'center' }}>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="body1" gutterBottom>
              {file ? file.name : 'Drag and drop an image here, or click to select'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {file ? 'Click to change image' : 'Supports: JPG, PNG, GIF (max 10MB)'}
            </Typography>
          </Box>
        </Box>

        {/* Show uploaded image preview as soon as a file is selected, before prompts */}
        {file && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Uploaded Image Preview
            </Typography>
            <Box
              component="img"
              src={URL.createObjectURL(file)}
              alt="Uploaded"
              sx={{ width: '100%', height: 'auto', borderRadius: 1 }}
            />
          </Paper>
        )}

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Example Prompts:
          </Typography>
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
            {EXAMPLE_PROMPTS.map((prompt) => (
              <Chip
                key={prompt}
                label={prompt}
                onClick={() => handlePresetClick(prompt)}
                sx={{ m: 0.5 }}
                disabled={uploading}
              />
            ))}
          </Stack>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <TextField
            fullWidth
            label="Style Description"
            multiline
            rows={3}
            value={styleDescription}
            onChange={(e) => setStyleDescription(e.target.value)}
            placeholder="Describe the style of your preset..."
            disabled={uploading}
            error={!!error && error.message === 'No style description'}
            helperText={error?.message === 'No style description' ? error.details : ''}
          />
          <Button
            variant="outlined"
            startIcon={<PresetIcon />}
            onClick={generatePreset}
            sx={{ minWidth: '150px' }}
            disabled={uploading}
          >
            Surprise Me
          </Button>
        </Box>

        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            onClose={() => setError(null)}
          >
            <Typography variant="subtitle2">{error.message}</Typography>
            {error.details && (
              <Typography variant="body2">{error.details}</Typography>
            )}
          </Alert>
        )}

        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={uploading || !file || !styleDescription.trim()}
          fullWidth
        >
          {uploading ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Generating Preset...
            </>
          ) : (
            'Generate Preset'
          )}
        </Button>
      </Paper>

      {/* Show XMP download and start over only after result is available */}
      {result && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Preset Generated!
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadXMP}
            >
              Download XMP
            </Button>
            <Button
              variant="outlined"
              onClick={handleStartOver}
            >
              Start Over
            </Button>
          </Box>
        </Paper>
      )}

      <Snackbar
        open={showSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message="Operation completed successfully"
      />
    </>
  );
};

export default StyleUploader; 