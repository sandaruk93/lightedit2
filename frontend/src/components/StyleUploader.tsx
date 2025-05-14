import React, { useState, useCallback, useEffect } from 'react';
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
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
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
  const [presetOptions, setPresetOptions] = useState<string[]>([]);
  const [selectedPreset, setSelectedPreset] = useState('');

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

  // Fetch preset options from backend CSV (or hardcode for now)
  useEffect(() => {
    // For now, hardcode the list (should be fetched from backend ideally)
    setPresetOptions([
      'Cinematic Teal & Orange',
      'Moody Forest',
      'Urban Grit',
      'Golden Hour Glow',
      'Film Matte Fade',
      'Pastel Pop',
      'Vintage Sepia',
      'Retro 90s Camcorder',
      'Soft Skin Portrait',
      'Vibrant Boost',
      'Clean Light Airy',
      'Earth Tones',
      'Coastal Cool',
      'Foggy Minimal',
      'Black & White Contrast',
      'Custom Warm + Contrast + Dehaze',
    ]);
  }, []);

  const handlePresetChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedPreset(event.target.value);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!file) {
      setError({
        message: 'No file selected',
        details: 'Please select an image to process'
      });
      return;
    }
    if (!selectedPreset) {
      setError({
        message: 'No preset selected',
        details: 'Please select a preset style to continue.'
      });
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('style_description', selectedPreset);

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
      setSelectedPreset('');
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
    setSelectedPreset('');
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

        {/* Preset selection as Chips */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Select a Preset Style
          </Typography>
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
            {presetOptions.map((preset) => (
              <Chip
                key={preset}
                label={preset}
                clickable
                color={selectedPreset === preset ? 'primary' : 'default'}
                variant={selectedPreset === preset ? 'filled' : 'outlined'}
                onClick={() => {
                  setSelectedPreset(preset);
                  setError(null);
                }}
                disabled={uploading}
                sx={{ m: 0.5, fontWeight: selectedPreset === preset ? 'bold' : 'normal' }}
              />
            ))}
          </Stack>
        </Box>

        {/* Surprise Me Button */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
          <Button
            variant="contained"
            startIcon={<PresetIcon />}
            onClick={() => {
              if (presetOptions.length > 0) {
                const random = presetOptions[Math.floor(Math.random() * presetOptions.length)];
                setSelectedPreset(random);
                setError(null);
              }
            }}
            disabled={uploading || presetOptions.length === 0}
            sx={{
              background: 'linear-gradient(90deg, #ff9800 0%, #ff5722 100%)',
              color: 'white',
              fontWeight: 'bold',
              borderRadius: 3,
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              boxShadow: 3,
              textTransform: 'uppercase',
              letterSpacing: 1,
              transition: 'all 0.2s',
              '&:hover': {
                background: 'linear-gradient(90deg, #ff5722 0%, #ff9800 100%)',
                boxShadow: 6,
                transform: 'scale(1.05)',
              },
            }}
          >
            Surprise Me!
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
          disabled={uploading || !file || !selectedPreset}
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