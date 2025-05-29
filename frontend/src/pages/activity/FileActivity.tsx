import React, { useEffect, useState } from 'react';

interface FileActivityData {
  id: number;
  user_email: string;
  file_path: string;
  action: string;
  timestamp: string;
  ip_address?: string;
  is_anomalous: boolean;
  details?: string;
}

const FileActivity: React.FC = () => {
  const [activities, setActivities] = useState<FileActivityData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState({
    action: '',
    is_anomalous: '',
  });

  // Fetch file activities with auto-refresh
  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const token = localStorage.getItem('token');
        const params = new URLSearchParams();
        if (filter.action) params.append('action', filter.action);
        if (filter.is_anomalous !== '') params.append('is_anomalous', filter.is_anomalous);
        
        const response = await fetch(
          `http://localhost:8000/api/v1/activities/files?${params}`,
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
        console.error('Failed to fetch file activities:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchActivities();
    // Auto-refresh every 3 seconds
    const interval = setInterval(fetchActivities, 3000);
    
    return () => clearInterval(interval);
  }, [filter]);

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'VIEW':
        return (
          <svg className="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        );
      case 'DOWNLOAD':
        return (
          <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
        );
      case 'UPLOAD':
        return (
          <svg className="h-5 w-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        );
      case 'DELETE':
        return (
          <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        );
      case 'MODIFY':
        return (
          <svg className="h-5 w-5 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        );
      default:
        return (
          <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
    }
  };

  const getFileTypeIcon = (filePath: string) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'xlsx':
      case 'xls':
        return '📊';
      case 'docx':
      case 'doc':
        return '📝';
      case 'pptx':
      case 'ppt':
        return '📑';
      case 'zip':
      case 'rar':
        return '📦';
      case 'csv':
        return '📈';
      default:
        return '📎';
    }
  };

  if (isLoading) {
    return <div className="p-4 flex justify-center">Loading file activities...</div>;
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">File Activity</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            Monitoring file operations
          </span>
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Action Type
            </label>
            <select
              value={filter.action}
              onChange={(e) => setFilter({ ...filter, action: e.target.value })}
              className="w-full border border-gray-300 rounded-md p-2"
            >
              <option value="">All Actions</option>
              <option value="VIEW">View</option>
              <option value="DOWNLOAD">Download</option>
              <option value="UPLOAD">Upload</option>
              <option value="DELETE">Delete</option>
              <option value="MODIFY">Modify</option>
            </select>
          </div>
          
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
              onClick={() => setFilter({ action: '', is_anomalous: '' })}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>
      
      {/* Activities List */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {activities.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No file activities found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    File
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    IP Address
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
                      <div className="flex items-center">
                        {getActionIcon(activity.action)}
                        <span className="ml-2 text-sm text-gray-900">{activity.action}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="flex items-center">
                        <span className="mr-2 text-lg">{getFileTypeIcon(activity.file_path)}</span>
                        <div>
                          <div className="font-medium">{activity.file_path.split('/').pop()}</div>
                          <div className="text-gray-500 text-xs">{activity.file_path}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.user_email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(activity.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.ip_address || 'N/A'}
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
      <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Activities</h3>
          <p className="text-2xl font-semibold">{activities.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-medium text-gray-500">Downloads</h3>
          <p className="text-2xl font-semibold text-green-600">
            {activities.filter(a => a.action === 'DOWNLOAD').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-medium text-gray-500">Deletions</h3>
          <p className="text-2xl font-semibold text-red-600">
            {activities.filter(a => a.action === 'DELETE').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="text-sm font-medium text-gray-500">Suspicious</h3>
          <p className="text-2xl font-semibold text-orange-600">
            {activities.filter(a => a.is_anomalous).length}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FileActivity;