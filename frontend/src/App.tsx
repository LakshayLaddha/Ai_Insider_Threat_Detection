import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AuthLayout from './components/layout/AuthLayout';
import LoginPage from './pages/auth/LoginPage';
import './index.css';

// Placeholder Dashboard component until we build the real one
const DashboardPage = () => (
  <div className="p-6">
    <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
    <p>Welcome to the Sentinel Security Dashboard!</p>
  </div>
);

const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Auth routes */}
          <Route path="/" element={<AuthLayout />}>
            <Route index element={<Navigate to="/login" />} />
            <Route path="login" element={<LoginPage />} />
          </Route>

          {/* Simple dashboard route - will enhance later */}
          <Route path="/dashboard" element={<DashboardPage />} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;