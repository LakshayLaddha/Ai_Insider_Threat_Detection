import React from 'react';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import LinearProgress from '@mui/material/LinearProgress';
import Avatar from '@mui/material/Avatar';
import PersonIcon from '@mui/icons-material/Person';
import { red, orange, green } from '@mui/material/colors';

const ThreatCard = ({ threat }) => {
  // Determine threat level color
  const getThreatColor = (score) => {
    if (score >= 0.7) return red[500];
    if (score >= 0.4) return orange[500];
    return green[500];
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <Card 
      sx={{ 
        mb: 2, 
        border: 1, 
        borderColor: getThreatColor(threat.threat_score),
        boxShadow: `0 0 10px ${getThreatColor(threat.threat_score)}40`
      }}
    >
      <CardHeader
        avatar={
          <Avatar sx={{ bgcolor: getThreatColor(threat.threat_score) }}>
            <PersonIcon />
          </Avatar>
        }
        title={
          <Typography variant="h6">
            {threat.user_id}
            <Chip 
              label={threat.threat_score > 0.7 ? "High Risk" : threat.threat_score > 0.4 ? "Medium Risk" : "Low Risk"} 
              size="small" 
              sx={{ 
                ml: 1, 
                bgcolor: getThreatColor(threat.threat_score),
                color: 'white'
              }} 
            />
          </Typography>
        }
        subheader={`${formatTime(threat.timestamp)} | ${threat.ip_address}`}
      />
      <CardContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Action: {threat.action} | Resource: {threat.resource}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Typography variant="body2" sx={{ mr: 1, minWidth: 120 }}>
              Threat Score:
            </Typography>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={threat.threat_score * 100} 
                sx={{ 
                  height: 8, 
                  borderRadius: 5,
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getThreatColor(threat.threat_score)
                  }
                }}
              />
            </Box>
            <Typography variant="body2">
              {Math.round(threat.threat_score * 100)}%
            </Typography>
          </Box>
        </Box>
        
        {threat.reasons && threat.reasons.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Reasons:
            </Typography>
            <Box component="ul" sx={{ pl: 2, mt: 0 }}>
              {threat.reasons.map((reason, index) => (
                <Typography component="li" variant="body2" key={index} sx={{ mb: 0.5 }}>
                  {reason}
                </Typography>
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ThreatCard;