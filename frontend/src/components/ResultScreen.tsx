import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  CircularProgress,
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';

interface ResultScreenProps {
  originalImage: string;
  editedImage: string;
  styleDescription: string;
  isProcessing: boolean;
  onDownloadXMP: () => void;
  onDownloadEdited: () => void;
  onStartOver: () => void;
}

const ResultScreen: React.FC<ResultScreenProps> = ({
  originalImage,
  editedImage,
  styleDescription,
  isProcessing,
  onDownloadXMP,
  onDownloadEdited,
  onStartOver,
}) => {
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Style Preview
      </Typography>

      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Style: {styleDescription}
      </Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Original Image
            </Typography>
            <Box
              component="img"
              src={originalImage}
              alt="Original"
              sx={{
                width: '100%',
                height: 'auto',
                borderRadius: 1,
              }}
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Edited Preview
            </Typography>
            {isProcessing ? (
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  minHeight: '200px',
                }}
              >
                <CircularProgress />
              </Box>
            ) : (
              <Box
                component="img"
                src={editedImage}
                alt="Edited"
                sx={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: 1,
                }}
              />
            )}
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={onDownloadXMP}
          disabled={isProcessing}
        >
          Download XMP
        </Button>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={onDownloadEdited}
          disabled={isProcessing}
        >
          Download Image
        </Button>
        <Button
          variant="outlined"
          onClick={onStartOver}
          disabled={isProcessing}
        >
          Start Over
        </Button>
      </Box>
    </Paper>
  );
};

export default ResultScreen; 