import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/auth/LoginPage';
import Dashboard from './pages/dashboard/DashboardPage';
import Layout from './components/layout/Layout';
import Alerts from './pages/Alerts';
import UserManagement from './pages/UserManagement';
import LoginActivity from './pages/activity/LoginActivity';
import FileActivity from './pages/activity/FileActivity';
import Settings from './pages/Settings';
import ThreatSimulator from './pages/admin/ThreatSimulator';

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      {/* Protected routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="activity/logins" element={<LoginActivity />} />
        <Route path="activity/files" element={<FileActivity />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="settings" element={<Settings />} />
        {/* Added Threat Simulator route */}
        <Route path="simulator" element={<ThreatSimulator />} />
      </Route>
      
      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;