import React from 'react';

interface ActivityChartProps {
  data: any[];
}

const ActivityChart: React.FC<ActivityChartProps> = ({ data }) => {
  return (
    <div className="bg-gray-100 rounded p-4 flex items-center justify-center" style={{ height: '300px' }}>
      <div className="text-center">
        <p className="text-gray-500">Activity line chart would appear here.</p>
        <p className="text-gray-500 text-sm mt-2">
          {data.length > 0 
            ? `Showing data for ${data.length} days` 
            : 'No activity data available'}
        </p>
      </div>
    </div>
  );
};

export default ActivityChart;