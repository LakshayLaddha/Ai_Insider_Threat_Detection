import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { red, orange, blue, green } from '@mui/material/colors';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import PersonIcon from '@mui/icons-material/Person';
import RouterIcon from '@mui/icons-material/Router';

const StatCard = ({ title, value, icon, color, subtitle }) => (
  <Paper 
    elevation={3} 
    sx={{ 
      p: 2, 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      borderLeft: `4px solid ${color}`,
      backgroundColor: 'background.paper'
    }}
  >
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <Box>
        <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
          {value}
        </Typography>
        <Typography color="text.secondary" variant="body2">
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      <Box 
        sx={{ 
          backgroundColor: `${color}20`, 
          borderRadius: '50%', 
          p: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {icon}
      </Box>
    </Box>
  </Paper>
);

const ThreatStats = ({ stats }) => {
  const {
    total_logs_analyzed = 0,
    threat_count = 0,
    threat_percentage = 0,
    top_users = [],
    top_ips = []
  } = stats || {};

  // Get top user and IP if available
  const topUser = top_users && top_users.length > 0 ? top_users[0] : null;
  const topIp = top_ips && top_ips.length > 0 ? top_ips[0] : null;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Total Logs Analyzed"
          value={total_logs_analyzed}
          icon={<SecurityIcon sx={{ color: blue[500] }} />}
          color={blue[500]}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Detected Threats"
          value={threat_count}
          icon={<WarningIcon sx={{ color: red[500] }} />}
          color={red[500]}
          subtitle={`${threat_percentage.toFixed(1)}% of total activity`}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Most Flagged User"
          value={topUser ? topUser.user_id : "None"}
          icon={<PersonIcon sx={{ color: orange[500] }} />}
          color={orange[500]}
          subtitle={topUser ? `${topUser.threat_count} threats detected` : "No threats detected"}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Most Flagged IP"
          value={topIp ? topIp.ip_address : "None"}
          icon={<RouterIcon sx={{ color: green[500] }} />}
          color={green[500]}
          subtitle={topIp ? `${topIp.threat_count} threats detected` : "No threats detected"}
        />
      </Grid>
    </Grid>
  );
};

export default ThreatStats;