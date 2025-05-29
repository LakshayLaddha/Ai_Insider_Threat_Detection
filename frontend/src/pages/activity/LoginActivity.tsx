import React, { useEffect, useState } from 'react';

interface LoginActivityData {
  id: number;
  user_email: string;
  ip_address: string;
  user_agent?: string;
  country?: string;
  city?: string;
  timestamp: string;
  success: boolean;
  is_anomalous: boolean;
}

const LoginActivity: React.FC = () => {
  const [activities, setActivities] = useState<LoginActivityData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState({
    is_anomalous: '',
  });

  // Fetch login activities with auto-refresh
  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const token = localStorage.getItem('token');
        const params = new URLSearchParams();
        if (filter.is_anomalous !== '') {
          params.append('is_anomalous', filter.is_anomalous);
        }
        
        const response = await fetch(
          `http://localhost:8000/api/v1/activities/logins?${params}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          setActivities(data);
        }
      } catch (error) {
        console.error('Failed to fetch login activities:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchActivities();
    // Auto-refresh every 3 seconds
    const interval = setInterval(fetchActivities, 3000);
    
    return () => clearInterval(interval);
  }, [filter]);

  const getStatusIcon = (success: boolean) => {
    if (success) {
      return (
        <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    } else {
      return (
        <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
  };

  if (isLoading) {
    return <div className="p-4 flex justify-center">Loading login activities...</div>;
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Login Activity</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            Live monitoring active
          </span>
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Activity Type
            </label>
            <select
              value={filter.is_anomalous}
              onChange={(e) => setFilter({ ...filter, is_anomalous: e.target.value })}
              className="w-full border border-gray-300 rounded-md p-2"
            >
              <option value="">All Activities</option>
              <option value="false">Normal</option>
              <option value="true">Suspicious</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => setFilter({ is_anomalous: '' })}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>
      
      {/* Activities Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {activities.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No login activities found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    IP Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activities.map((activity) => (
                  <tr key={activity.id} className={activity.is_anomalous ? 'bg-red-50' : ''}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusIcon(activity.success)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {activity.user_email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.ip_address}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.city && activity.country 
                        ? `${activity.city}, ${activity.country}`
                        : 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(activity.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {activity.is_anomalous ? (
                        <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
                          Suspicious
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                          Normal
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* Activity Summary */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Logins</h3>
          <p className="text-2xl font-semibold">{activities.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-medium text-gray-500">Failed Attempts</h3>
          <p className="text-2xl font-semibold text-red-600">
            {activities.filter(a => !a.success).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-medium text-gray-500">Suspicious Activities</h3>
          <p className="text-2xl font-semibold text-orange-600">
            {activities.filter(a => a.is_anomalous).length}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginActivity;