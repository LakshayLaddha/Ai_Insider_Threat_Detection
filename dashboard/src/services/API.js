import axios from 'axios';

// API base URL - adjust based on your deployment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://api:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service methods
const API = {
  // Health checks
  getHealth: () => {
    return apiClient.get('/health');
  },
  
  // Model information
  getModelInfo: () => {
    return apiClient.get('/model/info');
  },
  
  // Predictions
  predictThreat: (logEntry) => {
    return apiClient.post('/predict', logEntry);
  },
  
  // Batch predictions
  predictBatch: (logEntries) => {
    return apiClient.post('/predict/batch', logEntries);
  },
  
  // Get recent predictions
  getRecentPredictions: (limit = 10) => {
    return apiClient.get(`/predictions/recent?limit=${limit}`);
  },
  
  // Get threat analytics
  getThreatAnalytics: () => {
    return apiClient.get('/analytics/threats');
  },
  
  // Simulate a log entry for testing
  simulateLogEntry: () => {
    // Generate a random log entry
    const users = ['user_1', 'user_2', 'user_3', 'user_12', 'user_18'];
    const actions = ['READ', 'WRITE', 'LOGIN', 'DOWNLOAD', 'DELETE'];
    const resources = ['S3_BUCKET', 'EC2_INSTANCE', 'RDS_DATABASE', 'IAM_ROLE'];
    const ips = [
      '192.168.1.105', 
      '10.0.0.123', 
      '172.16.0.5',
      '8.8.8.8',  // Google DNS (unusual)
      '203.0.113.42' // TEST-NET-3 (unusual)
    ];
    
    // Use an unusual IP with low probability for anomalies
    const useUnusualIP = Math.random() < 0.2;
    const ipIndex = useUnusualIP ? Math.floor(Math.random() * 2) + 3 : Math.floor(Math.random() * 3);
    
    // Sometimes use unusual hours (night time)
    const useUnusualHour = Math.random() < 0.15;
    let now = new Date();
    if (useUnusualHour) {
      now.setHours(Math.floor(Math.random() * 5)); // 0-4 AM
    }
    
    const logEntry = {
      user_id: users[Math.floor(Math.random() * users.length)],
      action: actions[Math.floor(Math.random() * actions.length)],
      timestamp: now.toISOString(),
      resource: resources[Math.floor(Math.random() * resources.length)],
      ip_address: ips[ipIndex],
      data_size: Math.floor(Math.random() * 1000000) // 0-1MB
    };
    
    // For DELETE action, sometimes create a large data transfer
    if (logEntry.action === 'DELETE' && Math.random() < 0.3) {
      logEntry.data_size = Math.floor(Math.random() * 50000000) + 10000000; // 10-60MB
    }
    
    return apiClient.post('/predict', logEntry);
  }
};

export default API;