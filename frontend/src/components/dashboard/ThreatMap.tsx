import React from 'react';

interface ThreatMapProps {
  data: any[];
}

const ThreatMap: React.FC<ThreatMapProps> = ({ data }) => {
  return (
    <div className="bg-gray-100 rounded p-4 flex items-center justify-center" style={{ height: '300px' }}>
      <div className="text-center">
        <p className="text-gray-500">World map with threat origins would appear here.</p>
        <p className="text-gray-500 text-sm mt-2">
          {data.length > 0 
            ? `Showing ${data.length} threat points` 
            : 'No threat data available'}
        </p>
      </div>
    </div>
  );
};

export default ThreatMap;