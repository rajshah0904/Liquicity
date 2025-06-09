import React, { createContext, useState, useContext, useEffect } from 'react';
import { getCurrentUser, setCurrentUser } from '../utils/auth';
import api from '../utils/api';

// Create the context
const UserContext = createContext();

// Provider component
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on initial render
  useEffect(() => {
    const loadUser = () => {
      try {
        const userData = getCurrentUser();
        if (userData) {
          setUser(userData);
        }
      } catch (error) {
        console.error('Error loading user:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  // Fetch user data from API
  const fetchUserData = async () => {
    try {
      const response = await api.get('/user/user/');
      if (response.status === 200) {
        const userData = response.data;
        setUser(userData);
        setCurrentUser(userData);
        return userData;
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
      return null;
    }
  };

  // Update user data
  const updateUser = (newUserData) => {
    const updatedUser = { ...user, ...newUserData };
    setUser(updatedUser);
    setCurrentUser(updatedUser);
    return updatedUser;
  };

  // Clear user data (for logout)
  const clearUser = () => {
    setUser(null);
  };

  // Value object to be provided to consumers
  const value = {
    user,
    loading,
    updateUser,
    fetchUserData,
    clearUser
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

// Export context hook
export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export default UserContext; 