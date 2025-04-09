import React from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';
import { Paper, Typography, Box } from '@mui/material';

const ThreatChart = ({ data, chartType = 'line' }) => {
  // Format date for X axis
  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Process data to group by hour for the chart
  const processThreatData = (threats) => {
    if (!threats || threats.length === 0) {
      return [];
    }

    // Group by hour
    const groupedByHour = {};
    
    threats.forEach(threat => {
      const date = new Date(threat.timestamp);
      const hourKey = date.toISOString().slice(0, 13);
      
      if (!groupedByHour[hourKey]) {
        groupedByHour[hourKey] = {
          time: date,
          threats: 0,
          avgScore: 0,
          totalScore: 0
        };
      }
      
      groupedByHour[hourKey].threats += 1;
      groupedByHour[hourKey].totalScore += threat.threat_score;
      groupedByHour[hourKey].avgScore = groupedByHour[hourKey].totalScore / groupedByHour[hourKey].threats;
    });
    
    // Convert to array for chart
    return Object.values(groupedByHour).map(item => ({
      time: formatDate(item.time),
      threats: item.threats,
      avgScore: parseFloat(item.avgScore.toFixed(2))
    })).sort((a, b) => new Date(a.time) - new Date(b.time));
  };

  const chartData = processThreatData(data);

  const renderChart = () => {
    if (chartType === 'line') {
      return (
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis yAxisId="left" orientation="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="threats" stroke="#8884d8" activeDot={{ r: 8 }} name="Threats" />
          <Line yAxisId="right" type="monotone" dataKey="avgScore" stroke="#82ca9d" name="Avg Score" />
        </LineChart>
      );
    } else {
      return (
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="threats" fill="#8884d8" name="Threats" />
        </BarChart>
      );
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" component="h2" gutterBottom>
        Threat Activity Timeline
      </Typography>
      <Box sx={{ height: 300, mt: 2 }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartData.length > 0 ? (
            renderChart()
          ) : (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100%' 
            }}>
              <Typography variant="body1" color="text.secondary">
                No threat data available
              </Typography>
            </Box>
          )}
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default ThreatChart;