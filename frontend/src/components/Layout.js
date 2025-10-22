import React, { useState } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Button,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalanceWallet as WalletIcon,
  Send as SendIcon,
  CallReceived as ReceiveIcon,
  AccountBalance as VirtualAccountIcon,
  Receipt as TransactionsIcon,
  Person,
  Settings as SettingsIcon,
  Logout,
  Payment as PaymentsIcon,
  RequestQuote as RequestIcon,
  KeyboardArrowDown,
} from '@mui/icons-material';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState(null);
  const [paymentsOpen, setPaymentsOpen] = useState(false);
  
  // Mock user data - replace with actual user context
  const user = { name: 'Raj Shah' };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    navigate('/profile');
    handleMenuClose();
  };

  const handleSettings = () => {
    navigate('/settings');
    handleMenuClose();
  };

  const handleLogout = () => {
    handleMenuClose();
    // Add logout logic here
    navigate('/login');
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Wallet', icon: <WalletIcon />, path: '/wallet' },
    { text: 'Send', icon: <SendIcon />, path: '/payments/send' },
    { text: 'Receive', icon: <ReceiveIcon />, path: '/receive' },
    { text: 'Virtual Account', icon: <VirtualAccountIcon />, path: '/virtual-account' },
    { text: 'Transactions', icon: <TransactionsIcon />, path: '/transactions' },
  ];

  const paymentsSubmenu = [
    { text: 'Send Money', icon: <SendIcon />, path: '/payments/send' },
    { text: 'Request Money', icon: <RequestIcon />, path: '/payments/request' },
  ];

  const otherItems = [
    { text: 'Profile', icon: <Person />, path: '/profile' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
    { text: 'Logout', icon: <Logout />, path: '/logout' },
  ];

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#ffffff' }}>
      {/* Top Bar - Full width with logo on left */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: 72,
          bgcolor: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 4,
          zIndex: 1100,
        }}
      >
        {/* Logo */}
        <Typography 
          variant="h5" 
          sx={{ 
            fontWeight: 700, 
            color: '#000000', 
            fontSize: '1.5rem',
            letterSpacing: '-0.5px',
            cursor: 'pointer',
          }}
          onClick={() => navigate('/dashboard')}
        >
          Liquicity
        </Typography>

        {/* Right side - Promo button + User */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            variant="contained"
            sx={{
              bgcolor: '#37b24d',
              color: '#fff',
              px: 2.5,
              py: 1,
              fontSize: '0.875rem',
              fontWeight: 600,
              borderRadius: 2,
              textTransform: 'none',
              boxShadow: 'none',
              '&:hover': {
                bgcolor: '#2f9e44',
                boxShadow: 'none',
              },
            }}
          >
            Earn US$115
          </Button>

          <Box
            onClick={handleMenuOpen}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              cursor: 'pointer',
              px: 2,
              py: 1,
              borderRadius: 3,
              transition: 'all 0.2s',
              '&:hover': {
                bgcolor: '#f5f5f5',
              },
            }}
          >
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                bgcolor: '#d0d0d0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#333',
                fontSize: '0.875rem',
                fontWeight: 600,
              }}
            >
              {user?.name?.substring(0, 2).toUpperCase() || 'RS'}
            </Box>
            <Typography variant="body2" sx={{ fontWeight: 500, color: '#333', fontSize: '0.9375rem' }}>
              {user?.name || 'Raj Shah'}
            </Typography>
            <KeyboardArrowDown sx={{ color: '#666', fontSize: 20 }} />
          </Box>
        </Box>
      </Box>

      {/* Sidebar */}
      <Box
        sx={{
          width: 280,
          bgcolor: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          position: 'fixed',
          top: 72,
          left: 0,
          height: 'calc(100vh - 72px)',
          overflowY: 'auto',
          pt: 3,
        }}
      >
        {/* Main Navigation */}
        <List sx={{ px: 2.5, pb: 0 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: '100px',
                  py: 1.25,
                  px: 2.5,
                  '&.Mui-selected': {
                    bgcolor: '#e8e8e8',
                    '&:hover': {
                      bgcolor: '#e8e8e8',
                    },
                  },
                  '&:hover': {
                    bgcolor: '#f5f5f5',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: location.pathname === item.path ? '#333' : '#666' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '1rem',
                    fontWeight: location.pathname === item.path ? 500 : 400,
                    color: '#333',
                    fontFamily: 'sans-serif',
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}

          {/* Payments with submenu - Commented out for now
          <ListItem disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              onClick={() => setPaymentsOpen(!paymentsOpen)}
              sx={{
                borderRadius: '100px',
                py: 1.25,
                px: 2.5,
                '&:hover': {
                  bgcolor: '#f5f5f5',
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40, color: '#666' }}>
                <PaymentsIcon />
              </ListItemIcon>
              <ListItemText
                primary="Payments"
                primaryTypographyProps={{
                  fontSize: '1rem',
                  fontWeight: 400,
                  color: '#333',
                  fontFamily: 'sans-serif',
                }}
              />
              <KeyboardArrowDown
                sx={{
                  transform: paymentsOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s',
                  fontSize: 20,
                  color: '#666',
                }}
              />
            </ListItemButton>
          </ListItem>

          {paymentsOpen && (
            <Box sx={{ pl: 2 }}>
              {paymentsSubmenu.map((item) => (
                <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                  <ListItemButton
                    onClick={() => navigate(item.path)}
                    sx={{
                      borderRadius: '100px',
                      py: 1.25,
                      px: 2.5,
                      '&:hover': {
                        bgcolor: '#f5f5f5',
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36, color: '#666' }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={item.text}
                      primaryTypographyProps={{
                        fontSize: '0.9375rem',
                        fontWeight: 400,
                        color: '#555',
                        fontFamily: 'sans-serif',
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </Box>
          )}
          */}

          {/* Bottom section items */}
          <Box sx={{ mt: 'auto', pt: 2 }}>
            {otherItems.map((item) => (
              <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  onClick={() => {
                    if (item.path === '/logout') {
                      handleLogout();
                    } else {
                      navigate(item.path);
                    }
                  }}
                  sx={{
                    borderRadius: '100px',
                    py: 1.25,
                    px: 2.5,
                    '&:hover': {
                      bgcolor: '#f5f5f5',
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40, color: '#666' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{
                      fontSize: '1rem',
                      fontWeight: 400,
                      color: '#333',
                      fontFamily: 'sans-serif',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </Box>
        </List>
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: '280px',
          mt: '72px',
          bgcolor: '#ffffff',
          minHeight: 'calc(100vh - 72px)',
        }}
      >
        <Box sx={{ px: 5, py: 4 }}>{children || <Outlet />}</Box>
      </Box>

      {/* User Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{
          sx: { mt: 1, minWidth: 180, borderRadius: 2 },
        }}
      >
        <MenuItem onClick={handleProfile} sx={{ py: 1.5 }}>
          <ListItemIcon>
            <Person fontSize="small" />
          </ListItemIcon>
          <ListItemText>Profile</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleSettings} sx={{ py: 1.5 }}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout} sx={{ py: 1.5 }}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          <ListItemText>Logout</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Layout;
