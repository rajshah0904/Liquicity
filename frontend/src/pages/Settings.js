import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Divider, 
  Box, 
  TextField, 
  Button, 
  Grid,
  Switch,
  FormControlLabel,
  Alert,
  Stack,
  Tabs,
  Tab,
  Avatar,
  CircularProgress,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Badge,
  styled
} from '@mui/material';
import { 
  Person as PersonIcon, 
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Edit as EditIcon,
  ExpandMore as ExpandMoreIcon,
  Phone as PhoneIcon,
  Home as HomeIcon,
  LocationOn as LocationOnIcon,
  Fingerprint as FingerprintIcon,
  CameraAlt as CameraIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import countries from '../utils/countries';

// Interface for TabPanel
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Add this styled component for the file input
const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const Settings = () => {
  const { currentUser, refreshUser, logout, setCurrentUser } = useAuth();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  
  // Profile state
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    date_of_birth: '',
    phone_number: '',
    country: '',
    country_code: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    avatar_url: '',
    bio: ''
  });
  
  // Password change state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  // Notification settings state
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: false,
    marketingEmails: false,
    transactionAlerts: true,
    largeTransactionAlerts: false,
    minTransactionAmount: 100,
    productUpdates: true
  });
  
  // Add these state variables to the Settings component
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState('');
  
  // Load user data when component mounts
  useEffect(() => {
    if (currentUser?.id) {
      setFormData({
        name: currentUser.name || '',
        email: currentUser.email || '',
        bio: currentUser.bio || '',
        location: currentUser.location || '',
        avatar: currentUser.avatar || ''
      });
      
      // Fetch notification settings
      fetchNotificationSettings();
    }
  }, [currentUser]);
  
  const loadUserData = async () => {
    setLoading(true);
    
    try {
      // Load profile information
      const profileData = {
        first_name: '',
        last_name: '',
        email: currentUser?.email || '',
        date_of_birth: '',
        phone_number: '',
        country: '',
        country_code: currentUser?.country_code || '',
        address_line1: '',
        address_line2: '',
        city: '',
        state: '',
        postal_code: '',
        avatar_url: '',
        bio: ''
      };
      
      // Extract profile data from user object if it exists
      if (currentUser?.profile) {
        Object.keys(profileData).forEach(key => {
          if (currentUser.profile[key] !== undefined) {
            profileData[key] = currentUser.profile[key];
          }
        });
      }
      
      setProfileForm(profileData);
      
      // Load notification settings
      if (currentUser?.id) {
        try {
          const response = await api.get(`/user/notification-settings/${currentUser.id}`);
          if (response.data) {
            setNotificationSettings(response.data);
          }
        } catch (settingsError) {
          console.error('Error loading notification settings', settingsError);
          // Continue with default notification settings
        }
      }
    } catch (error) {
      console.error('Error loading user data', error);
      setMessage({
        type: 'error',
        text: 'Error loading your profile information'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleProfileChange = (e) => {
    setProfileForm({
      ...profileForm,
      [e.target.name]: e.target.value
    });
  };

  const handlePasswordChange = (e) => {
    setPasswordForm({
      ...passwordForm,
      [e.target.name]: e.target.value
    });
  };

  const handleNotificationChange = (event) => {
    const { name, value, checked } = event.target;
    setNotificationSettings((prev) => ({
      ...prev,
      [name]: value !== undefined ? value : checked,
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    try {
      if (!currentUser?.id) {
        throw new Error('User ID not found');
      }
      
      const response = await api.put(`/user/profile/${currentUser.id}`, profileForm);
      
      if (response.status === 200) {
        // Update the currentUser context with the new profile data
        const updatedUser = {
          ...currentUser,
          profile: {
            ...(currentUser.profile || {}),
            ...profileForm
          }
        };
        
        if (setCurrentUser) {
          setCurrentUser(updatedUser);
        }
        
        setMessage({
          type: 'success',
          text: 'Profile updated successfully'
        });
      }
    } catch (error) {
      console.error('Error updating profile', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Error updating profile'
      });
    } finally {
      setLoading(false);
    }
  };

  const submitPasswordChange = async (e) => {
    e.preventDefault();
    
    // Password validation
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setMessage({
        type: 'error',
        text: 'New passwords do not match'
      });
      return;
    }
    
    if (passwordForm.new_password.length < 8) {
      setMessage({
        type: 'error',
        text: 'Password must be at least 8 characters'
      });
      return;
    }
    
    setLoading(true);
    
    try {
      await api.put(`/user/update-password/${currentUser.id}`, {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      });

    setMessage({
      type: 'success',
      text: 'Password updated successfully'
    });
    
    // Reset form
    setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      
    } catch (error) {
      console.error('Error updating password', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to update password'
      });
    } finally {
      setLoading(false);
    }
  };

  const saveNotificationSettings = async () => {
    setLoading(true);
    try {
      // Mock API call - replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log('Notification settings saved:', notificationSettings);
      toast.success('Notification preferences updated successfully');
    } catch (error) {
      console.error('Error saving notification settings:', error);
      toast.error('Failed to update notification preferences');
    } finally {
      setLoading(false);
    }
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Add these functions to the Settings component
  const handleAvatarChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setAvatarFile(file);
      
      // Create a preview URL
      const previewUrl = URL.createObjectURL(file);
      setAvatarPreview(previewUrl);
    }
  };

  const uploadAvatar = async () => {
    if (!avatarFile) return;
    
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', avatarFile);
      
      const response = await api.post(`/user/upload-avatar/${currentUser.id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data && response.data.avatar_url) {
        // Update profile form with new avatar URL
        setProfileForm({
          ...profileForm,
          avatar_url: response.data.avatar_url
        });
        
    setMessage({
      type: 'success',
          text: 'Profile picture updated successfully'
        });
        
        // Refresh user data
        await refreshUser();
      }
    } catch (error) {
      console.error('Error uploading avatar', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to upload profile picture'
      });
    } finally {
      setLoading(false);
      // Clean up preview URL
      if (avatarPreview) {
        URL.revokeObjectURL(avatarPreview);
        setAvatarPreview('');
      }
      setAvatarFile(null);
    }
  };

  // Function to fetch notification settings
  const fetchNotificationSettings = async () => {
    if (!currentUser?.id) return;
    
    try {
      const response = await api.get(`/user/notification-settings/${currentUser.id}`);
      if (response.status === 200 && response.data) {
        setNotificationSettings(response.data);
      }
    } catch (error) {
      console.error('Error fetching notification settings:', error);
      // Use default values instead of showing error
    }
  };

  if (loading && !currentUser) {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 2 }}>
        Account Settings
      </Typography>
      
      {message && (
        <Alert 
          severity={message.type} 
          sx={{ mb: 3 }}
          onClose={() => setMessage(null)}
        >
          {message.text}
        </Alert>
      )}
      
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="settings tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab icon={<PersonIcon />} iconPosition="start" label="Profile" />
            <Tab icon={<SecurityIcon />} iconPosition="start" label="Security" />
            <Tab icon={<NotificationsIcon />} iconPosition="start" label="Notifications" />
          </Tabs>
        </Box>
        
        {/* Profile Tab */}
        <TabPanel value={tabValue} index={0}>
          <Paper sx={{ p: 3 }}>
            <form onSubmit={handleSubmit}>
              <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Badge
                    overlap="circular"
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                    badgeContent={
                      <IconButton 
                        component="label" 
                        sx={{ 
                          backgroundColor: 'primary.main',
                          color: 'white',
                          '&:hover': { backgroundColor: 'primary.dark' }
                        }}
                        size="small"
                      >
                        <CameraIcon fontSize="small" />
                        <VisuallyHiddenInput 
                          type="file" 
                          accept="image/*"
                          onChange={handleAvatarChange}
                        />
                      </IconButton>
                    }
                  >
                    <Avatar 
                      src={avatarPreview || profileForm.avatar_url || undefined} 
                      sx={{ width: 80, height: 80, mr: 2 }} 
                    />
                  </Badge>
                  <Box>
                    <Typography variant="h6">
                      {currentUser?.username || 'User'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {currentUser?.email || 'No email provided'}
                    </Typography>
                  </Box>
                </Box>
                {avatarFile && (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button 
                      variant="contained" 
                      size="small"
                      onClick={uploadAvatar}
                      disabled={loading}
                    >
                      {loading ? <CircularProgress size={20} /> : 'Upload New Photo'}
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => {
                        setAvatarFile(null);
                        if (avatarPreview) {
                          URL.revokeObjectURL(avatarPreview);
                          setAvatarPreview('');
                        }
                      }}
                    >
                      Cancel
                    </Button>
                  </Box>
                )}
              </Box>
              
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <PersonIcon sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Personal Information</Typography>
                </AccordionSummary>
                <AccordionDetails>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
                        label="First Name"
                        name="first_name"
                        value={profileForm.first_name}
                        onChange={handleProfileChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Last Name"
                        name="last_name"
                        value={profileForm.last_name}
                        onChange={handleProfileChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Email"
                        name="email"
                        type="email"
                        value={profileForm.email}
                        onChange={handleProfileChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Date of Birth"
                        name="date_of_birth"
                        type="date"
                        value={profileForm.date_of_birth}
                        onChange={handleProfileChange}
                        InputLabelProps={{
                          shrink: true,
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Bio"
                        name="bio"
                        value={profileForm.bio}
                        onChange={handleProfileChange}
                        multiline
                        rows={3}
                      />
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <PhoneIcon sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Contact Information</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Phone Number"
                        name="phone_number"
                        value={profileForm.phone_number}
                        onChange={handleProfileChange}
            />
          </Grid>
        </Grid>
                </AccordionDetails>
              </Accordion>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <HomeIcon sx={{ mr: 1 }} />
                  <Typography variant="subtitle1">Address Information</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Address Line 1"
                        name="address_line1"
                        value={profileForm.address_line1}
                        onChange={handleProfileChange}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Address Line 2"
                        name="address_line2"
                        value={profileForm.address_line2}
                        onChange={handleProfileChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="City"
                        name="city"
                        value={profileForm.city}
                        onChange={handleProfileChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="State/Province"
                        name="state"
                        value={profileForm.state}
                        onChange={handleProfileChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Postal Code"
                        name="postal_code"
                        value={profileForm.postal_code}
                        onChange={handleProfileChange}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        select
                        label="Country"
                        name="country"
                        value={profileForm.country}
                        onChange={handleProfileChange}
                      >
                        {countries.map((country) => (
                          <MenuItem key={country.code} value={country.name}>
                            {country.name}
                          </MenuItem>
                        ))}
                      </TextField>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                <Button 
                  variant="contained" 
                  color="primary" 
                  type="submit"
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Save Profile'}
                </Button>
              </Box>
            </form>
      </Paper>
        </TabPanel>
      
        {/* Security Tab */}
        <TabPanel value={tabValue} index={1}>
          <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Change Password
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <form onSubmit={submitPasswordChange}>
          <Stack spacing={3}>
            <TextField
              fullWidth
              type="password"
              label="Current Password"
                  name="current_password"
                  value={passwordForm.current_password}
              onChange={handlePasswordChange}
              required
            />
            <TextField
              fullWidth
              type="password"
              label="New Password"
                  name="new_password"
                  value={passwordForm.new_password}
              onChange={handlePasswordChange}
              required
                  helperText="Password must be at least 8 characters"
            />
            <TextField
              fullWidth
              type="password"
              label="Confirm New Password"
                  name="confirm_password"
                  value={passwordForm.confirm_password}
              onChange={handlePasswordChange}
              required
            />
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    type="submit" 
                    variant="contained"
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Update Password'}
              </Button>
            </Box>
          </Stack>
        </form>
      </Paper>
      
          <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
              Account Security
        </Typography>
        <Divider sx={{ mb: 3 }} />
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                <FingerprintIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Account Access
              </Typography>
              
              <Button 
                variant="outlined" 
                color="error" 
                onClick={handleLogout}
                sx={{ mt: 1 }}
              >
                Log Out of All Devices
              </Button>
            </Box>
          </Paper>
        </TabPanel>
        
        {/* Notifications Tab */}
        <TabPanel value={tabValue} index={2}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Notification Preferences
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="medium">
                Account Notifications
              </Typography>
              <Box sx={{ mb: 2 }}>
        <FormControlLabel
          control={
            <Switch
                      checked={notificationSettings.emailNotifications}
                      onChange={handleNotificationChange}
              name="emailNotifications"
                      color="primary"
            />
          }
          label="Email Notifications"
        />
                <Typography variant="caption" color="text.secondary">
                  Receive important updates about your account and transactions via email
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.pushNotifications}
                      onChange={handleNotificationChange}
                      name="pushNotifications"
                      color="primary"
                    />
                  }
                  label="Push Notifications"
                />
                <Typography variant="caption" color="text.secondary">
                  Get real-time alerts on your device about transactions, deposits, and withdrawals.
                </Typography>
              </Box>
              
              <Typography variant="subtitle1" gutterBottom fontWeight="medium" sx={{ mt: 3 }}>
                Transaction Notifications
        </Typography>
        
              <Box sx={{ pl: 2, mt: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.transactionAlerts}
                      onChange={handleNotificationChange}
                      name="transactionAlerts"
                      color="primary"
                    />
                  }
                  label="Transaction Alerts"
                />
                <Typography variant="caption" color="text.secondary">
                  Receive notifications for every transaction over $0.
                </Typography>
              </Box>
              
              <Box sx={{ pl: 2, mt: 2 }}>
        <FormControlLabel
          control={
            <Switch
                      checked={notificationSettings.largeTransactionAlerts}
              onChange={handleNotificationChange}
                      name="largeTransactionAlerts"
                      color="primary"
                    />
                  }
                  label="Large Transaction Alerts"
                />
                <Typography variant="caption" color="text.secondary">
                  Get alerts only for transactions over a certain amount.
                </Typography>
                {notificationSettings.largeTransactionAlerts && (
                  <TextField
                    label="Minimum Amount ($)"
                    variant="outlined"
                    type="number"
                    size="small"
                    name="minTransactionAmount"
                    value={notificationSettings.minTransactionAmount}
                    onChange={(e) => handleNotificationChange({
                      target: {
                        name: e.target.name,
                        value: parseFloat(e.target.value)
                      }
                    })}
                    sx={{ ml: 4, mt: 1, width: '200px' }}
                    disabled={!notificationSettings.largeTransactionAlerts}
                  />
                )}
              </Box>
              
              <Typography variant="subtitle1" gutterBottom fontWeight="medium" sx={{ mt: 3 }}>
                Communication Preferences
        </Typography>
        
              <Box sx={{ mb: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.marketingEmails}
                      onChange={handleNotificationChange}
                      name="marketingEmails"
                      color="primary"
                    />
                  }
                  label="Marketing Emails"
                />
                <Typography variant="caption" color="text.secondary">
                  Stay updated with our latest features, promotions, and news. You can unsubscribe anytime.
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.productUpdates}
                      onChange={handleNotificationChange}
                      name="productUpdates"
                      color="primary"
                    />
                  }
                  label="Product Updates"
                />
                <Typography variant="caption" color="text.secondary">
                  Receive notifications about new features and improvements to the platform.
                </Typography>
              </Box>
              
              <Box sx={{ mt: 3 }}>
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={saveNotificationSettings}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Save Preferences'}
          </Button>
              </Box>
        </Box>
      </Paper>
        </TabPanel>
      </Box>
    </Container>
  );
};

export default Settings; 