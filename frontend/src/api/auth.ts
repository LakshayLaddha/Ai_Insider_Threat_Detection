import { api } from './client';
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL!;


// Replace your current login function with this
export const loginUser = async (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append('username', email); // IMPORTANT: Use 'username' field for email
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/api/v1/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  return response.json();
};