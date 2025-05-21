import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'block' : 'hidden'} md:block md:w-64 bg-gray-800 text-white`}>
        <div className="p-4">
          <h2 className="text-xl font-bold">Sentinel Security</h2>
        </div>
        
        <nav className="mt-4">
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => 
              `block py-2 px-4 ${isActive ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-700'}`
            }
          >
            Dashboard
          </NavLink>
          
          <NavLink 
            to="/alerts" 
            className={({ isActive }) => 
              `block py-2 px-4 ${isActive ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-700'}`
            }
          >
            Alerts
          </NavLink>
          
          <NavLink 
            to="/activity/logins" 
            className={({ isActive }) => 
              `block py-2 px-4 ${isActive ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-700'}`
            }
          >
            Login Activity
          </NavLink>
          
          <NavLink 
            to="/activity/files" 
            className={({ isActive }) => 
              `block py-2 px-4 ${isActive ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-700'}`
            }
          >
            File Activity
          </NavLink>
          
          {user?.is_admin && (
            <>
              <NavLink 
                to="/users" 
                className={({ isActive }) => 
                  `block py-2 px-4 ${isActive ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                User Management
              </NavLink>
              
              {/* Added Threat Simulator Link for Admins */}
              <NavLink 
                to="/simulator" 
                className={({ isActive }) => 
                  `block py-2 px-4 ${isActive ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                Threat Simulator
              </NavLink>
            </>
          )}
          
          <NavLink 
            to="/settings" 
            className={({ isActive }) => 
              `block py-2 px-4 ${isActive ? 'bg-gray-700 text-white' : 'text-gray-300 hover:bg-gray-700'}`
            }
          >
            Settings
          </NavLink>
        </nav>
      </div>
      
      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="flex items-center justify-between p-4">
            <button 
              onClick={toggleSidebar}
              className="md:hidden p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <div className="ml-auto flex items-center">
              <span className="mr-4 text-gray-700">{user?.full_name || user?.username}</span>
              <button 
                onClick={logout}
                className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Logout
              </button>
            </div>
          </div>
        </header>
        
        {/* Content */}
        <main className="flex-1 overflow-y-auto bg-gray-100">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;