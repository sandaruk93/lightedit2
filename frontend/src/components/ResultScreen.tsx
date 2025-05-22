import React, { useEffect } from 'react';
import { Box, Button, Typography, Paper, CircularProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

const ResultContainer = styled(Paper)(({ theme }) => ({
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

const PreviewImage = styled('img')({
  width: '100%',
  maxHeight: 400,
  objectFit: 'contain',
  borderRadius: 8,
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
});

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

interface ResultScreenProps {
  presetId: string;
  styleDescription: string;
  xmpUrl: string;
  previewUrl: string;
  onStartOver: () => void;
}

const ResultScreen: React.FC<ResultScreenProps> = ({
  presetId,
  styleDescription,
  xmpUrl,
  previewUrl,
  onStartOver,
}) => {
  useEffect(() => {
    // Automatically download the preset file when the component mounts
    const downloadPreset = async () => {
      try {
        const response = await fetch(xmpUrl);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${styleDescription.toLowerCase().replace(/\s+/g, '-')}.xmp`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (error) {
        console.error('Error downloading preset:', error);
      }
    };

    downloadPreset();
  }, [xmpUrl, styleDescription]);

  return (
    <ResultContainer elevation={3}>
      <Typography variant="h4" component="h2" gutterBottom align="center" sx={{ fontWeight: 600 }}>
        Preset Generated Successfully!
      </Typography>
      
      <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 2 }}>
        Your "{styleDescription}" preset has been created and downloaded automatically.
      </Typography>

      <PreviewImage src={previewUrl} alt="Preview" />

      <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
        <StyledButton
          variant="contained"
          color="primary"
          onClick={onStartOver}
          startIcon={<RestartAltIcon />}
          sx={{
            backgroundColor: '#2196f3',
            '&:hover': {
              backgroundColor: '#1976d2',
            },
          }}
        >
          Start Over
        </StyledButton>
      </Box>
    </ResultContainer>
  );
};

export default ResultScreen; 