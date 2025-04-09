import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  TextField, 
  Button, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import API from '../services/API';

const Settings = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Mock settings
  const [alertThreshold, setAlertThreshold] = useState(0.7);
  const [autoRefresh, setAutoRefresh] = useState(30);
  
  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const response = await API.getModelInfo();
        setModelInfo(response.data);
      } catch (error) {
        console.error("Error fetching model info:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchModelInfo();
  }, []);
  
  const handleSaveSettings = () => {
    // In a real app, this would save to backend
    alert("Settings saved successfully!");
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Dashboard Settings
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel id="refresh-label">Auto Refresh Interval</InputLabel>
                  <Select
                    labelId="refresh-label"
                    value={autoRefresh}
                    label="Auto Refresh Interval"
                    onChange={(e) => setAutoRefresh(e.target.value)}
                  >
                    <MenuItem value={0}>Disabled</MenuItem>
                    <MenuItem value={15}>15 seconds</MenuItem>
                    <MenuItem value={30}>30 seconds</MenuItem>
                    <MenuItem value={60}>1 minute</MenuItem>
                    <MenuItem value={300}>5 minutes</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Threat Alert Threshold"
                  type="number"
                  value={alertThreshold}
                  onChange={(e) => setAlertThreshold(parseFloat(e.target.value))}
                  inputProps={{ min: 0, max: 1, step: 0.05 }}
                  helperText="Scores above this threshold will trigger alerts (0-1)"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={handleSaveSettings}
                >
                  Save Settings
                </Button>
              </Grid>
            </Grid>
          </Paper>
          
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              API Status
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            <Alert severity="success" sx={{ mb: 2 }}>
              API service is running normally
            </Alert>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              API Endpoint: http://localhost:8000
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Model Information
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            {loading ? (
              <Typography>Loading model information...</Typography>
            ) : modelInfo ? (
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Model Type" 
                    secondary={modelInfo.model_type} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Training Date" 
                    secondary={new Date(modelInfo.training_date).toLocaleString()} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Feature Count" 
                    secondary={modelInfo.feature_count} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Contamination Rate" 
                    secondary={`${modelInfo.contamination * 100}%`} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Number of Estimators" 
                    secondary={modelInfo.n_estimators} 
                  />
                </ListItem>
              </List>
            ) : (
              <Alert severity="error">
                Failed to load model information
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;