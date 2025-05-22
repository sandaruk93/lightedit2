import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import ResultScreen from './ResultScreen';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const UploadContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: theme.spacing(3),
  maxWidth: 600,
  margin: '0 auto',
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  borderRadius: theme.spacing(2),
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
}));

const UploadBox = styled('label')(({ theme }) => ({
  width: '100%',
  height: 200,
  border: `2px dashed ${theme.palette.primary.main}`,
  borderRadius: theme.spacing(2),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  gap: theme.spacing(2),
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  backgroundColor: 'rgba(33, 150, 243, 0.05)',
  '&:hover': {
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
    borderColor: theme.palette.primary.dark,
  },
}));

const StyledButton = styled(Button)(({ theme }) => ({
  padding: theme.spacing(1.5, 4),
  borderRadius: theme.spacing(2),
  textTransform: 'none',
  fontSize: '1.1rem',
  fontWeight: 600,
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
  },
}));

const StyleUploader: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [styleDescription, setStyleDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    presetId: string;
    styleDescription: string;
    xmpUrl: string;
    previewUrl: string;
  } | null>(null);
  const [recommendedPreset, setRecommendedPreset] = useState<string | null>(null);
  const [confidenceScore, setConfidenceScore] = useState<number | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size should be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setError(null);

    // Analyze image and get preset recommendation
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/recommend_preset/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze image');
      }

      const data = await response.json();
      setRecommendedPreset(data.preset);
      setConfidenceScore(data.confidence_score);
    } catch (error) {
      console.error('Error analyzing image:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !styleDescription) {
      setError('Please select a file and enter a style description');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('style_description', styleDescription);

      const response = await fetch(`${API_URL}/generate_preset/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to generate preset');
      }

      const data = await response.json();
      setResult({
        presetId: data.preset_id,
        styleDescription: data.style_description,
        xmpUrl: `${API_URL}${data.xmp_url}`,
        previewUrl: `${API_URL}${data.preview_url}`,
      });
    } catch (error) {
      setError('Failed to generate preset. Please try again.');
      console.error('Error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleStartOver = () => {
    setSelectedFile(null);
    setStyleDescription('');
    setResult(null);
    setError(null);
    setRecommendedPreset(null);
    setConfidenceScore(null);
  };

  if (result) {
    return (
      <ResultScreen
        presetId={result.presetId}
        styleDescription={result.styleDescription}
        xmpUrl={result.xmpUrl}
        previewUrl={result.previewUrl}
        onStartOver={handleStartOver}
      />
    );
  }

  return (
    <UploadContainer elevation={3}>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ fontWeight: 600 }}>
        Create Lightroom Preset
      </Typography>

      <UploadBox htmlFor="file-upload">
        <input
          id="file-upload"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main' }} />
        <Typography variant="h6" color="primary">
          {selectedFile ? selectedFile.name : 'Click to upload image'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supported formats: JPG, PNG, HEIC
        </Typography>
      </UploadBox>

      <TextField
        fullWidth
        label="Style Description"
        value={styleDescription}
        onChange={(e) => setStyleDescription(e.target.value)}
        placeholder="e.g., Moody Forest, Urban Grit, Golden Hour"
        variant="outlined"
        sx={{ mt: 2 }}
      />

      {recommendedPreset && (
        <Alert 
          severity="info" 
          icon={<LightbulbIcon />}
          sx={{ width: '100%', mt: 2 }}
        >
          Recommended preset: <strong>{recommendedPreset}</strong>
          {confidenceScore && ` (${Math.round(confidenceScore * 100)}% confidence)`}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ width: '100%', mt: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
        <StyledButton
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!selectedFile || !styleDescription || isUploading}
          sx={{
            backgroundColor: '#2196f3',
            '&:hover': {
              backgroundColor: '#1976d2',
            },
          }}
        >
          {isUploading ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Generating Preset...
            </>
          ) : (
            'Generate Preset'
          )}
        </StyledButton>
      </Box>
    </UploadContainer>
  );
};

export default StyleUploader; 