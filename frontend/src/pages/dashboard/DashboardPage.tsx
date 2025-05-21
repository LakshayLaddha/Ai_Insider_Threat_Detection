import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import StatCard from '../../components/dashboard/StatCard';
import AlertsList from '../../components/dashboard/AlertsList';
import ActivityChart from '../../components/dashboard/ActivityChart';
import ThreatMap from '../../components/dashboard/ThreatMap';


const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    totalAlerts: 0,
    criticalAlerts: 0,
    loginAttempts: 0,
    failedLogins: 0,
    recentThreats: [],
    activityData: [],
  });
  const [isLoading, setIsLoading] = useState(true);

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/v1/dashboard', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setDashboardData(data);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <div className="p-4 flex justify-center">Loading dashboard data...</div>;
  }

  return (
    <div className="px-4 py-6">
      <h1 className="text-2xl font-semibold mb-6">Dashboard</h1>
      
      {/* Welcome message */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <h2 className="text-lg font-medium mb-2">Welcome, {user?.full_name || user?.username}!</h2>
        <p>Here's the current security status of your system.</p>
      </div>
      
      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard 
          title="Total Alerts" 
          value={dashboardData.totalAlerts} 
          icon="bell" 
          change={+2}
          color="blue" 
        />
        <StatCard 
          title="Critical Alerts" 
          value={dashboardData.criticalAlerts} 
          icon="warning" 
          change={+1}
          color="red" 
        />
        <StatCard 
          title="Login Attempts" 
          value={dashboardData.loginAttempts} 
          icon="login" 
          change={+5}
          color="green" 
        />
        <StatCard 
          title="Failed Logins" 
          value={dashboardData.failedLogins} 
          icon="shield" 
          change={-1}
          color="yellow" 
        />
      </div>
      
      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-lg font-medium mb-4">Login Activity (Last 7 days)</h3>
          <ActivityChart data={dashboardData.activityData} />
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-lg font-medium mb-4">Threat Detection Map</h3>
          <ThreatMap data={dashboardData.recentThreats} />
        </div>
      </div>
      
      {/* Recent alerts */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <h3 className="text-lg font-medium mb-4">Recent Security Alerts</h3>
        <AlertsList alerts={dashboardData.recentThreats} />
      </div>
    </div>
  );
};

export default Dashboard;