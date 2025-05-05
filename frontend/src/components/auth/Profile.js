import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const Profile = () => {
  const { user, isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return <div>Loading user profile...</div>;
  }

  if (!isAuthenticated || !user) {
    return <div>Please log in to view your profile</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        {user.picture && (
          <img
            src={user.picture}
            alt="Profile"
            className="profile-picture"
            width="50"
            height="50"
          />
        )}
        <div className="profile-details">
          <h2>{user.name}</h2>
          <p className="email">{user.email}</p>
        </div>
      </div>
      
      {/* Additional user details */}
      <div className="user-details">
        <div className="detail-item">
          <span className="label">Email verified:</span>
          <span className="value">{user.email_verified ? 'Yes' : 'No'}</span>
        </div>
        
        {user.nickname && (
          <div className="detail-item">
            <span className="label">Nickname:</span>
            <span className="value">{user.nickname}</span>
          </div>
        )}
        
        {user.updated_at && (
          <div className="detail-item">
            <span className="label">Last update:</span>
            <span className="value">{new Date(user.updated_at).toLocaleDateString()}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile; 