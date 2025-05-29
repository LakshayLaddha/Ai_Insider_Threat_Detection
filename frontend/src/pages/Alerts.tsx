import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface Alert {
  id: number;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  source_ip?: string;
  location?: string;
  resolved: boolean;
}

const Alerts: React.FC = () => {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState({
    severity: '',
    resolved: '',
  });

  // Fetch alerts with auto-refresh
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const token = localStorage.getItem('token');
        const params = new URLSearchParams();
        if (filter.severity) params.append('severity', filter.severity);
        if (filter.resolved !== '') params.append('resolved', filter.resolved);
        
        const response = await fetch(
          `http://localhost:8000/api/v1/activities/alerts?${params}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          setAlerts(data);
        }
      } catch (error) {
        console.error('Failed to fetch alerts:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAlerts();
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchAlerts, 5000);
    
    return () => clearInterval(interval);
  }, [filter]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const resolveAlert = async (alertId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/activities/alerts/${alertId}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ resolved: true }),
        }
      );
      
      if (response.ok) {
        // Update local state
        setAlerts(alerts.map(alert => 
          alert.id === alertId ? { ...alert, resolved: true } : alert
        ));
      }
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  if (isLoading) {
    return <div className="p-4 flex justify-center">Loading alerts...</div>;
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Security Alerts</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            Auto-refreshing every 5 seconds
          </span>
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Severity
            </label>
            <select
              value={filter.severity}
              onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
              className="w-full border border-gray-300 rounded-md p-2"
            >
              <option value="">All Severities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filter.resolved}
              onChange={(e) => setFilter({ ...filter, resolved: e.target.value })}
              className="w-full border border-gray-300 rounded-md p-2"
            >
              <option value="">All Statuses</option>
              <option value="false">Open</option>
              <option value="true">Resolved</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => setFilter({ severity: '', resolved: '' })}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>
      
      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow-sm">
        {alerts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No alerts found. The system is secure.
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <div key={alert.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`px-2 py-1 text-xs rounded-full border ${getSeverityColor(alert.severity)}`}>
                        {alert.severity.toUpperCase()}
                      </span>
                      <span className="ml-3 text-sm font-medium text-gray-900">
                        {alert.alert_type}
                      </span>
                      {alert.resolved && (
                        <span className="ml-3 px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                          RESOLVED
                        </span>
                      )}
                    </div>
                    
                    <p className="text-gray-700 mb-2">{alert.message}</p>
                    
                    <div className="flex items-center text-sm text-gray-500 space-x-4">
                      <span>
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                      {alert.source_ip && (
                        <span>IP: {alert.source_ip}</span>
                      )}
                      {alert.location && (
                        <span>Location: {alert.location}</span>
                      )}
                    </div>
                  </div>
                  
                  {!alert.resolved && user?.is_admin && (
                    <button
                      onClick={() => resolveAlert(alert.id)}
                      className="ml-4 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;