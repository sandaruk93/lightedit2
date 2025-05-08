import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  CircularProgress,
  Divider,
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import axios from 'axios';
import StyleUploader from './components/StyleUploader';

const API_URL = 'http://localhost:8000';

interface FileMetadata {
  filename: string;
  style_description: string;
  upload_time: string;
}

function App() {
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/files/`);
      setFiles(response.data.files);
    } catch (error) {
      console.error('Error fetching files:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleDelete = async (filename: string) => {
    try {
      await axios.delete(`${API_URL}/files/${filename}`);
      fetchFiles();
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Style Upload System
        </Typography>

        <StyleUploader onUploadComplete={fetchFiles} />

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Uploaded Styles
          </Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <List>
              {files.map((file) => (
                <React.Fragment key={file.filename}>
                  <ListItem>
                    <ListItemText
                      primary={file.filename}
                      secondary={
                        <>
                          <Typography component="span" variant="body2" color="text.primary">
                            Style Description:
                          </Typography>
                          <br />
                          {file.style_description}
                          <br />
                          <Typography component="span" variant="caption" color="text.secondary">
                            Uploaded: {new Date(file.upload_time).toLocaleString()}
                          </Typography>
                        </>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => handleDelete(file.filename)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
              {files.length === 0 && (
                <ListItem>
                  <ListItemText primary="No files uploaded yet" />
                </ListItem>
              )}
            </List>
          )}
        </Paper>
      </Box>
    </Container>
  );
}

export default App; 