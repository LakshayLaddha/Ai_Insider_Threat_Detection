import React, { useState, useEffect } from 'react';
import { Grid, Typography, Paper, Box, Button } from '@mui/material';
import ThreatStats from '../components/ThreatStats';
import ThreatCard from '../components/ThreatCard';
import ThreatChart from '../components/ThreatChart';
import RefreshIcon from '@mui/icons-material/Refresh';
import API from '../services/API';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [threatStats, setThreatStats] = useState(null);
  const [recentThreats, setRecentThreats] = useState([]);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch threat analytics
      const statsResponse = await API.getThreatAnalytics();
      setThreatStats(statsResponse.data);
      
      // Fetch recent predictions
      const threatsResponse = await API.getRecentPredictions(5);
      setRecentThreats(threatsResponse.data);
      
      setLastRefreshed(new Date());
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchData();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Threat Dashboard
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />}
          onClick={fetchData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>
      
      <Box sx={{ mb: 1 }}>
        <Typography variant="caption" color="text.secondary">
          Last updated: {lastRefreshed.toLocaleString()}
        </Typography>
      </Box>
      
      {/* Stats Cards */}
      <Box sx={{ mb: 4 }}>
        <ThreatStats stats={threatStats} />
      </Box>
      
      <Grid container spacing={4}>
        {/* Chart */}
        <Grid item xs={12} md={8}>
          <ThreatChart data={recentThreats} />
        </Grid>
        
        {/* Recent Threats */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" component="h2" gutterBottom>
              Recent Threats
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              {recentThreats.filter(threat => threat.is_threat).length > 0 ? (
                recentThreats
                  .filter(threat => threat.is_threat)
                  .slice(0, 3)
                  .map(threat => (
                    <ThreatCard key={threat.log_id} threat={threat} />
                  ))
              ) : (
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No recent threats detected
                  </Typography>
                </Box>
              )}
              
              {recentThreats.filter(threat => threat.is_threat).length > 3 && (
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <Button variant="text" href="/threats">
                    View All Threats
                  </Button>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;