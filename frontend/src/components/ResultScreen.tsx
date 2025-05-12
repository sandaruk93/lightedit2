import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';

interface ResultScreenProps {
  originalImage: string;
  styleDescription: string;
  onDownloadXMP: () => void;
  onStartOver: () => void;
}

const ResultScreen: React.FC<ResultScreenProps> = ({
  originalImage,
  styleDescription,
  onDownloadXMP,
  onStartOver,
}) => {
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Uploaded Image Preview
      </Typography>

      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Style: {styleDescription}
      </Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Uploaded Image
            </Typography>
            <Box
              component="img"
              src={originalImage}
              alt="Uploaded"
              sx={{
                width: '100%',
                height: 'auto',
                borderRadius: 1,
              }}
            />
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={onDownloadXMP}
        >
          Download XMP
        </Button>
        <Button
          variant="outlined"
          onClick={onStartOver}
        >
          Start Over
        </Button>
      </Box>
    </Paper>
  );
};

export default ResultScreen; 