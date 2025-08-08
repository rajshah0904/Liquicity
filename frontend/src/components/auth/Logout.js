import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';

const LogoutButton = () => {
  const { logout } = useAuth0();
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear all Auth0 cache to prevent session interference with new signups
    localStorage.clear();
    sessionStorage.clear();
    
    // Simple logout and navigate
    logout();
    navigate('/login');
  };

  return (
    <button 
      onClick={handleLogout}
      className="btn btn-danger"
    >
      Log Out
    </button>
  );
};

export default LogoutButton; 