import React from 'react';
import { Outlet } from 'react-router-dom';

const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-3xl font-extrabold text-gray-900">
            Sentinel Security
          </h1>
          <h2 className="mt-2 text-center text-sm text-gray-600">
            Security Monitoring System
          </h2>
        </div>
        <Outlet />
      </div>
    </div>
  );
};

export default AuthLayout;