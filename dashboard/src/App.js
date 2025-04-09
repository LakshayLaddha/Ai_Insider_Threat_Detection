import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Pages
import Dashboard from './pages/Dashboard';
import ThreatList from './pages/ThreatList';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';
import TestConnection from './pages/TestConnection'; // Add this import

// Components
import Layout from './components/Layout';

// Create a theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/threats" element={<ThreatList />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/test" element={<TestConnection />} /> {/* Add this route */}
            <Route path="/404" element={<NotFound />} />
            <Route path="/" element={<Navigate replace to="/dashboard" />} />
            <Route path="*" element={<Navigate replace to="/404" />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;