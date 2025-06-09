import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

/**
 * ProtectedRoute component that checks if the user is authenticated
 * and redirects to login if not
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth0();

  // If authentication status is still loading, show nothing
  if (isLoading) {
    return null;
  }

  // If user is not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If user is authenticated, render the protected component
  return children;
};

export default ProtectedRoute; 