import { api } from './client';

// Dashboard-related API functions
export const getDashboardData = () => {
  return api.get('/api/v1/dashboard');
};

// Add empty export if there are no actual exports yet
// export {};