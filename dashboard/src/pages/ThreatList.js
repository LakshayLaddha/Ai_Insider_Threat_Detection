import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import ThreatCard from '../components/ThreatCard';
import RefreshIcon from '@mui/icons-material/Refresh';
import API from '../services/API';

const ThreatList = () => {
  const [loading, setLoading] = useState(true);
  const [threats, setThreats] = useState([]);
  const [filter, setFilter] = useState('all'); // all, high, medium, low
  
  const fetchThreats = async () => {
    setLoading(true);
    try {
      const response = await API.getRecentPredictions(100); // Get more threats for filtering
      setThreats(response.data);
    } catch (error) {
      console.error("Error fetching threats:", error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchThreats();
  }, []);
  
  // Apply filters to the threats list
  const filteredThreats = threats.filter(threat => {
    // Only show threats (not normal activity) unless viewing all
    if (filter !== 'all' && !threat.is_threat) return false;
    
    // Apply risk level filters
    if (filter === 'high') return threat.threat_score >= 0.7;
    if (filter === 'medium') return threat.threat_score >= 0.4 && threat.threat_score < 0.7;
    if (filter === 'low') return threat.threat_score < 0.4;
    
    return true;
  });
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Threat List
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />}
          onClick={fetchThreats}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={filter}
                label="Risk Level"
                onChange={(e) => setFilter(e.target.value)}
              >
                <MenuItem value="all">All Activity</MenuItem>
                <MenuItem value="high">High Risk</MenuItem>
                <MenuItem value="medium">Medium Risk</MenuItem>
                <MenuItem value="low">Low Risk</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Threat List */}
      <Box>
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography>Loading threats...</Typography>
          </Box>
        ) : filteredThreats.length > 0 ? (
          filteredThreats.map(threat => (
            <ThreatCard key={threat.log_id} threat={threat} />
          ))
        ) : (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography>No threats match the current filters</Typography>
          </Paper>
        )}
      </Box>
    </Box>
  );
};

export default ThreatList;