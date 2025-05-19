import React from 'react';

const DashboardPage: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-medium">Users</h2>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-medium">Login Activities</h2>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-medium">File Activities</h2>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-medium">Alerts</h2>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
      </div>
      <div className="mt-8 bg-white rounded-lg shadow p-4">
        <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
        <p className="text-gray-500">No recent activity</p>
      </div>
    </div>
  );
};

export default DashboardPage;