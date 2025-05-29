import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import StatCard from '../../components/dashboard/StatCard';
import AlertsList from '../../components/dashboard/AlertsList';
import ActivityChart from '../../components/dashboard/ActivityChart';
import ThreatMap from '../../components/dashboard/ThreatMap';

interface ActivityData {
  date: string;
  successful: number;
  failed: number;
}

interface DashboardAlert {
  id: number;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  source_ip?: string;
  location?: string;
  resolved: boolean;
}

interface DashboardData {
  totalAlerts: number;
  criticalAlerts: number;
  loginAttempts: number;
  failedLogins: number;
  recentThreats: DashboardAlert[];
  activityData: ActivityData[];
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    totalAlerts: 0,
    criticalAlerts: 0,
    loginAttempts: 0,
    failedLogins: 0,
    recentThreats: [],
    activityData: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Fetch dashboard data with auto-refresh
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
          setLastRefresh(new Date());
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    // Initial fetch
    fetchDashboardData();
    
    // Auto-refresh every 3 seconds
    const interval = setInterval(fetchDashboardData, 3000);
    
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  // Calculate percentage changes
  const calculateChange = (current: number, previous: number = 0) => {
    if (previous === 0) return current > 0 ? 100 : 0;
    return Math.round(((current - previous) / previous) * 100);
  };

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back, {user?.full_name || user?.username || user?.email}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            Live monitoring active
          </span>
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-400">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
        </div>
      </div>
      
      {/* System Status Banner */}
      <div className={`rounded-lg p-4 mb-6 ${
        dashboardData.criticalAlerts > 0 
          ? 'bg-red-50 border-l-4 border-red-500' 
          : 'bg-green-50 border-l-4 border-green-500'
      }`}>
        <div className="flex items-center">
          <div className="flex-1">
            <h2 className={`text-lg font-medium ${
              dashboardData.criticalAlerts > 0 ? 'text-red-800' : 'text-green-800'
            }`}>
              {dashboardData.criticalAlerts > 0 
                ? `⚠️ System Alert: ${dashboardData.criticalAlerts} critical issues detected`
                : '✅ System Secure: No critical issues detected'}
            </h2>
            <p className={`mt-1 text-sm ${
              dashboardData.criticalAlerts > 0 ? 'text-red-600' : 'text-green-600'
            }`}>
              {dashboardData.criticalAlerts > 0
                ? 'Immediate attention required for system security'
                : 'All systems operating normally'}
            </p>
          </div>
        </div>
      </div>
      
      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard 
          title="Total Alerts" 
          value={dashboardData.totalAlerts} 
          icon="bell" 
          change={0}
          color="blue" 
        />
        <StatCard 
          title="Critical Alerts" 
          value={dashboardData.criticalAlerts} 
          icon="warning" 
          change={0}
          color="red" 
        />
        <StatCard 
          title="Login Attempts" 
          value={dashboardData.loginAttempts} 
          icon="login" 
          change={0}
          color="green" 
        />
        <StatCard 
          title="Failed Logins" 
          value={dashboardData.failedLogins} 
          icon="shield" 
          change={0}
          color="yellow" 
        />
      </div>
      
      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium mb-4">Login Activity (Last 7 days)</h3>
          <ActivityChart data={dashboardData.activityData} />
          {dashboardData.activityData.length > 0 && (
            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
              <div className="text-center">
                <div className="text-gray-500">Total Successful</div>
                <div className="text-2xl font-semibold text-green-600">
                  {dashboardData.activityData.reduce((sum, day) => sum + day.successful, 0)}
                </div>
              </div>
              <div className="text-center">
                <div className="text-gray-500">Total Failed</div>
                <div className="text-2xl font-semibold text-red-600">
                  {dashboardData.activityData.reduce((sum, day) => sum + day.failed, 0)}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium mb-4">Threat Detection Map</h3>
          <ThreatMap data={dashboardData.recentThreats} />
          {dashboardData.recentThreats.length > 0 && (
            <div className="mt-4 text-sm text-gray-600">
              <p>Monitoring {dashboardData.recentThreats.length} potential threats</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {Array.from(new Set(dashboardData.recentThreats.map((t) => t.location)))
                  .slice(0, 5)
                  .map((location) => (
                    <span key={location} className="px-2 py-1 bg-gray-100 rounded text-xs">
                      {location}
                    </span>
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Recent alerts */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">Recent Security Alerts</h3>
          {dashboardData.recentThreats.length > 0 && (
            <span className="text-sm text-gray-500">
              Showing {Math.min(10, dashboardData.recentThreats.length)} of {dashboardData.totalAlerts} alerts
            </span>
          )}
        </div>
        <AlertsList alerts={dashboardData.recentThreats} />
      </div>
      
      {/* Quick Stats Summary */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-blue-500">
          <h4 className="text-sm font-medium text-gray-500">Security Score</h4>
          <div className="mt-2 flex items-baseline">
            <span className="text-3xl font-semibold text-gray-900">
              {dashboardData.criticalAlerts === 0 ? '98' : 
                dashboardData.criticalAlerts < 3 ? '75' : '45'}
            </span>
            <span className="ml-1 text-sm text-gray-500">/100</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Based on current threat level
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-green-500">
          <h4 className="text-sm font-medium text-gray-500">Success Rate</h4>
          <div className="mt-2 flex items-baseline">
            <span className="text-3xl font-semibold text-gray-900">
              {dashboardData.loginAttempts > 0 
                ? Math.round(((dashboardData.loginAttempts - dashboardData.failedLogins) / dashboardData.loginAttempts) * 100)
                : 100}
            </span>
            <span className="ml-1 text-sm text-gray-500">%</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Login success rate
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-orange-500">
          <h4 className="text-sm font-medium text-gray-500">Active Threats</h4>
          <div className="mt-2 flex items-baseline">
            <span className="text-3xl font-semibold text-gray-900">
              {dashboardData.recentThreats.filter((t) => !t.resolved).length}
            </span>
            <span className="ml-1 text-sm text-gray-500">unresolved</span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Requires immediate attention
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;