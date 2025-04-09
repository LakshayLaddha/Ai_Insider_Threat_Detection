import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Paper, CircularProgress } from '@mui/material';
import axios from 'axios';

const TestConnection = () => {
  const [apiStatus, setApiStatus] = useState('unknown');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  
  const testConnection = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiUrl}/health`);
      setApiStatus('connected');
      setResult(response.data);
    } catch (error) {
      console.error('API Connection Error:', error);
      setApiStatus('failed');
      setResult({
        error: true,
        message: error.message,
        details: error.response ? error.response.data : 'No response received'
      });
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    // Test connection on component mount
    testConnection();
  }, []);
  
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>API Connection Test</Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Status: 
          <Box component="span" sx={{ 
            ml: 1,
            color: apiStatus === 'connected' ? 'green' : 
                  apiStatus === 'failed' ? 'red' : 'orange'
          }}>
            {apiStatus === 'connected' ? 'Connected' : 
             apiStatus === 'failed' ? 'Failed' : 'Unknown'}
          </Box>
        </Typography>
        
        <Box sx={{ my: 2 }}>
          <Typography variant="body2" gutterBottom>
            API URL: {apiUrl}
          </Typography>
        </Box>
        
        <Button 
          variant="contained" 
          onClick={testConnection}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Testing...' : 'Test Connection'}
        </Button>
      </Paper>
      
      {result && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Response:</Typography>
          <pre style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '15px',
            borderRadius: '4px',
            overflow: 'auto'
          }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Paper>
      )}
    </Box>
  );
};

export default TestConnection;