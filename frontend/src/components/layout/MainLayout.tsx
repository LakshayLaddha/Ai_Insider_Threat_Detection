// src/components/layout/MainLayout.tsx
import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const MainLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-primary-600 text-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex-shrink-0">
            <h1 className="text-xl font-bold">Sentinel Security</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span>{user?.username || user?.email}</span>
            <button 
              onClick={handleLogout}
              className="bg-white text-primary-700 hover:bg-gray-100 px-3 py-1 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Sidebar and main content */}
      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r">
          <nav className="p-4">
            <ul className="space-y-2">
              <li>
                <Link 
                  to="/dashboard" 
                  className="block px-4 py-2 rounded hover:bg-primary-50 text-primary-700"
                >
                  Dashboard
                </Link>
              </li>
              <li>
                <Link 
                  to="/activities" 
                  className="block px-4 py-2 rounded hover:bg-primary-50 text-gray-700"
                >
                  Activities
                </Link>
              </li>
              <li>
                <Link 
                  to="/alerts" 
                  className="block px-4 py-2 rounded hover:bg-primary-50 text-gray-700"
                >
                  Alerts
                </Link>
              </li>
              <li>
                <Link 
                  to="/users" 
                  className="block px-4 py-2 rounded hover:bg-primary-50 text-gray-700"
                >
                  Users
                </Link>
              </li>
            </ul>
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6 bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;