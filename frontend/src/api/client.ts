// Base API client for making requests to the backend

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Function to get the auth token
const getToken = () => localStorage.getItem('token');

// Generic fetch function with authentication
export async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  // For all other error responses
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `API error: ${response.status} ${response.statusText}`
    );
  }

  // Return parsed JSON or empty object if no content
  return response.status !== 204 ? response.json() : ({} as T);
}

// API request helpers
export const api = {
  get: <T>(endpoint: string) => fetchWithAuth<T>(endpoint),
  
  post: <T>(endpoint: string, data: any) => 
    fetchWithAuth<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  put: <T>(endpoint: string, data: any) =>
    fetchWithAuth<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  delete: <T>(endpoint: string) =>
    fetchWithAuth<T>(endpoint, {
      method: 'DELETE',
    }),
};