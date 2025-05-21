import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

interface SimulationSettings {
  totalAttempts: number;
  threatPercentage: number;
  usernames: string[];
  locations: string[];
  startTime: string;
  endTime: string;
}

const ThreatSimulator: React.FC = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState<SimulationSettings>({
    totalAttempts: 20,
    threatPercentage: 10, // 10% - 2 out of 20 by default
    usernames: ['admin', 'john.doe', 'jane.smith', 'guest.user', 'support.team'],
    locations: ['US', 'CN', 'RU', 'IN', 'BR', 'DE', 'UK'],
    startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    endTime: new Date().toISOString().slice(0, 16)
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<{success: boolean; message: string; threatCount: number} | null>(null);
  const [presets, setPresets] = useState([
    { name: 'Case 1: Low Threat (10%)', percentage: 10 },
    { name: 'Case 2: No Threats (0%)', percentage: 0 },
    { name: 'Case 3: High Alert (75%)', percentage: 75 }
  ]);

  // Only allow admins
  if (!user?.is_admin) {
    return (
      <div className="px-4 py-6">
        <h1 className="text-2xl font-semibold mb-6">Threat Simulator</h1>
        <div className="bg-red-50 border-l-4 border-red-500 p-4">
          <p className="text-red-700">Admin access required</p>
        </div>
      </div>
    );
  }

  const handleSettingsChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    
    if (name === 'usernames' || name === 'locations') {
      // Handle arrays
      setSettings({
        ...settings,
        [name]: value.split(',').map(item => item.trim())
      });
    } else {
      // Handle regular fields
      setSettings({
        ...settings,
        [name]: type === 'number' ? Number(value) : value
      });
    }
  };

  const applyPreset = (percentage: number) => {
    setSettings({
      ...settings,
      threatPercentage: percentage
    });
  };

  const generateSimulation = async () => {
    setIsGenerating(true);
    setResult(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/simulator/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResult({
          success: true,
          message: `Successfully generated ${settings.totalAttempts} login attempts with ${data.threatCount} threats.`,
          threatCount: data.threatCount
        });
      } else {
        setResult({
          success: false,
          message: data.detail || 'Failed to generate simulation data.',
          threatCount: 0
        });
      }
    } catch (error) {
      setResult({
        success: false,
        message: 'An error occurred during simulation generation.',
        threatCount: 0
      });
      console.error('Simulation error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const simulateRealTimeLogin = async (isThreat: boolean) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/simulator/login', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          isThreat,
          username: settings.usernames[Math.floor(Math.random() * settings.usernames.length)]
        })
      });
      
      if (response.ok) {
        alert(`Successfully simulated a ${isThreat ? 'suspicious' : 'normal'} login attempt`);
      } else {
        const data = await response.json();
        alert(data.detail || 'Failed to simulate login');
      }
    } catch (error) {
      alert('An error occurred during login simulation');
      console.error('Login simulation error:', error);
    }
  };

  return (
    <div className="px-4 py-6">
      <h1 className="text-2xl font-semibold mb-6">Security Threat Simulator</h1>
      
      {/* Presets */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-medium mb-4">Quick Presets</h2>
        <div className="flex flex-wrap gap-2">
          {presets.map(preset => (
            <button
              key={preset.name}
              onClick={() => applyPreset(preset.percentage)}
              className="bg-blue-100 text-blue-800 px-3 py-2 rounded hover:bg-blue-200"
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>
      
      {/* Simulation Settings */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-medium mb-4">Simulation Settings</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Total Login Attempts
            </label>
            <input
              type="number"
              name="totalAttempts"
              min="1"
              max="100"
              value={settings.totalAttempts}
              onChange={handleSettingsChange}
              className="w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Threat Percentage ({Math.round(settings.totalAttempts * settings.threatPercentage / 100)} out of {settings.totalAttempts})
            </label>
            <input
              type="range"
              name="threatPercentage"
              min="0"
              max="100"
              value={settings.threatPercentage}
              onChange={handleSettingsChange}
              className="w-full"
            />
            <div className="text-sm text-gray-500 mt-1">
              {settings.threatPercentage}% of logins will be threats
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Usernames (comma-separated)
            </label>
            <textarea
              name="usernames"
              value={settings.usernames.join(', ')}
              onChange={handleSettingsChange}
              rows={2}
              className="w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Locations (country codes, comma-separated)
            </label>
            <textarea
              name="locations"
              value={settings.locations.join(', ')}
              onChange={handleSettingsChange}
              rows={2}
              className="w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Time
            </label>
            <input
              type="datetime-local"
              name="startTime"
              value={settings.startTime}
              onChange={handleSettingsChange}
              className="w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Time
            </label>
            <input
              type="datetime-local"
              name="endTime"
              value={settings.endTime}
              onChange={handleSettingsChange}
              className="w-full border border-gray-300 rounded-md p-2"
            />
          </div>
        </div>
        
        <div className="mt-6">
          <button
            onClick={generateSimulation}
            disabled={isGenerating}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
          >
            {isGenerating ? 'Generating...' : 'Generate Login Data'}
          </button>
        </div>
      </div>
      
      {/* Real-time Simulation */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-medium mb-4">Real-time Login Simulation</h2>
        <p className="mb-4 text-gray-600">
          Use these buttons to immediately add individual login events to the system for demonstration.
        </p>
        
        <div className="flex gap-4">
          <button
            onClick={() => simulateRealTimeLogin(false)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Simulate Normal Login
          </button>
          
          <button
            onClick={() => simulateRealTimeLogin(true)}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Simulate Suspicious Login
          </button>
        </div>
      </div>
      
      {/* Result */}
      {result && (
        <div className={`border-l-4 p-4 mb-6 ${
          result.success ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
        }`}>
          <p className={result.success ? 'text-green-700' : 'text-red-700'}>
            {result.message}
          </p>
          {result.success && (
            <p className="mt-2 font-medium">
              Generated {result.threatCount} threats ({(result.threatCount / settings.totalAttempts * 100).toFixed(1)}%)
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ThreatSimulator;