import React, { useState, useEffect, useMemo } from 'react';
import {
  Container,
  Typography,
  Box,
  ThemeProvider,
  createTheme,
  PaletteMode,
  CssBaseline,
} from '@mui/material';
import { ReactComponent as Logo } from './assets/logo.svg';
import StyleUploader from './components/StyleUploader';

const API_URL = 'http://localhost:8000';

function App() {
  const [mode, setMode] = useState<PaletteMode>('light');

  // Detect system preference for dark mode
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setMode(mediaQuery.matches ? 'dark' : 'light');

    const handleChange = (e: MediaQueryListEvent) => {
      setMode(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Create theme based on mode
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                // Light mode colors
                primary: {
                  main: '#1976d2',
                },
                background: {
                  default: '#f5f5f5',
                  paper: '#ffffff',
                },
              }
            : {
                // Dark mode colors
                primary: {
                  main: '#90caf9',
                },
                background: {
                  default: '#121212',
                  paper: '#1e1e1e',
                },
              }),
        },
        components: {
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
              },
            },
          },
        },
      }),
    [mode]
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <Logo style={{ width: 56, height: 56, marginRight: 16 }} />
            <Typography variant="h4" component="h1" gutterBottom align="center">
              AI Lightroom Preset Generator
            </Typography>
          </Box>
          <StyleUploader />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App; 