import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Box, 
  IconButton, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  ListItemButton,
  Avatar,
  useMediaQuery,
  useTheme,
  Menu,
  MenuItem,
  useScrollTrigger,
  Slide
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import LoginButton, { SignupButton } from './auth/Login';

// Icons
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import SendIcon from '@mui/icons-material/Send';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import QrCodeIcon from '@mui/icons-material/QrCode';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import LogoutIcon from '@mui/icons-material/Logout';


const navItems = [
  { path: '/dashboard', icon: <DashboardIcon />, text: 'Dashboard' },
  { path: '/wallet', icon: <AccountBalanceWalletIcon />, text: 'Wallet' },
  { path: '/payments/send', icon: <SendIcon />, text: 'Send' },
  { path: '/payments/request', icon: <QrCodeIcon />, text: 'Receive' },
  { path: '/virtual-account', icon: <AccountBalanceIcon />, text: 'Virtual Account' },
  { path: '/transactions', icon: <ReceiptLongIcon />, text: 'Transactions' },
];

function HideOnScroll({ children }) {
  const trigger = useScrollTrigger();

  return (
    <Slide appear={false} direction="down" in={!trigger}>
      {children}
    </Slide>
  );
}

const Navbar = ({ onDrawerToggle, drawerOpen, showMenuIcon = false }) => {
  // If drawerOpen prop is not provided, use local state
  const [localDrawerOpen, setLocalDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated, user, isLoading, logout } = useAuth0();

  // Use either prop or local state depending on what's provided
  const isDrawerOpen = drawerOpen !== undefined ? drawerOpen : localDrawerOpen;
  const isMenuOpen = Boolean(anchorEl);

  const toggleDrawer = () => {
    if (onDrawerToggle) {
      // Use parent's handler if provided
      onDrawerToggle();
    } else {
      // Otherwise use local state
      setLocalDrawerOpen(!localDrawerOpen);
    }
  };

  const handleLogout = () => {
    // Clear all Auth0 cache to prevent session interference with new signups
    localStorage.clear();
    sessionStorage.clear();
    
    // Simple logout and navigate
    logout();
    navigate('/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      // Close drawer on navigation for mobile
      toggleDrawer();
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogoutClick = () => {
    handleMenuClose();
    handleLogout();
  };


  return (
    <>
      <HideOnScroll>
        <AppBar 
          position="fixed" 
          sx={{
            zIndex: (theme) => theme.zIndex.drawer - 1,
            boxShadow: 'none',
            border: 'none',
            backgroundColor: '#ffffff'
          }}
        >
          <Toolbar sx={{ minHeight: '80px !important', height: '80px' }}>
            {showMenuIcon && (
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={toggleDrawer}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
            )}
            
            <Box sx={{ flexGrow: 1 }} />
            
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {isLoading ? (
                <div className="auth-loading">Loading...</div>
              ) : isAuthenticated ? (
                <>
                  <Box 
                    onClick={handleMenuOpen}
                    sx={{ 
                      display: 'flex', 
                      alignItems: 'center',
                      gap: 1.5,
                      cursor: 'pointer',
                      padding: '6px 12px',
                      borderRadius: '12px',
                      transition: 'background-color 0.2s',
                      '&:hover': {
                        bgcolor: '#f5f5f5'
                      }
                    }}
                  >
                    <Avatar 
                      src={user?.picture}
                      sx={{ 
                        width: 36, 
                        height: 36,
                        bgcolor: '#e0e0e0',
                        color: '#333',
                        fontSize: '0.875rem',
                        fontWeight: 600
                      }}
                    >
                      {user?.name?.split(' ').map(n => n[0]).join('').toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'}
                    </Avatar>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#1a1a1a', 
                        fontWeight: 500,
                        display: { xs: 'none', sm: 'block' }
                      }}
                    >
                      {user?.name || user?.email?.split('@')[0] || 'User'}
                    </Typography>
                    <KeyboardArrowDownIcon sx={{ color: '#666', fontSize: 20 }} />
                  </Box>
                  
                  <Menu
                    anchorEl={anchorEl}
                    open={isMenuOpen}
                    onClose={handleMenuClose}
                    onClick={handleMenuClose}
                    PaperProps={{
                      elevation: 0,
                      sx: {
                        overflow: 'visible',
                        filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.1))',
                        mt: 1.5,
                        minWidth: 200,
                        '& .MuiAvatar-root': {
                          width: 32,
                          height: 32,
                          ml: -0.5,
                          mr: 1,
                        },
                      },
                    }}
                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                  >
                    <MenuItem onClick={handleLogoutClick}>
                      <ListItemIcon>
                        <LogoutIcon fontSize="small" sx={{ color: '#666' }} />
                      </ListItemIcon>
                      <ListItemText>Logout</ListItemText>
                    </MenuItem>
                  </Menu>
                </>
              ) : (
                <div className="auth-buttons">
                  <LoginButton />
                  <SignupButton />
                </div>
              )}
            </Box>
          </Toolbar>
        </AppBar>
      </HideOnScroll>

      <Drawer
        variant={isMobile ? "temporary" : "permanent"}
        open={isMobile ? isDrawerOpen : true}
        onClose={isMobile ? toggleDrawer : undefined}
        sx={{
          width: 260,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { 
            width: 260, 
            boxSizing: 'border-box',
            paddingTop: '0',
            backgroundColor: '#ffffff',
            backdropFilter: 'blur(10px)',
            border: 'none',
            zIndex: (theme) => theme.zIndex.drawer + 2,
          },
        }}
      >
        {/* Logo at top center - aligned with AppBar height */}
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'flex-start', 
            alignItems: 'center',
            height: '80px',
            px: 2,
            pl: 3,
            mb: 4
          }}
        >
          <img 
            src="/images/Liquicity_Logo.png" 
            alt="Liquicity" 
            style={{ 
              width: '140px',
              height: 'auto'
            }} 
          />
        </Box>
        
        <Box sx={{ overflow: 'auto', py: 0 }}>
          <List sx={{ px: 1, pt: 0 }}>
            {navItems.map((item, index) => (
              <ListItem 
                key={item.path} 
                disablePadding 
                sx={{ 
                  display: 'block',
                  mb: 1.5,
                }}
              >
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    minHeight: 48,
                    justifyContent: 'initial',
                    px: 2.5,
                    mx: 1,
                    borderRadius: '12px',
                    transition: 'all 0.2s ease-in-out',
                    backgroundColor: location.pathname === item.path ? '#e8e8e8' : 'transparent',
                    '&:hover': {
                      backgroundColor: location.pathname === item.path ? '#e0e0e0' : '#f0f0f0',
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: 2,
                      justifyContent: 'center',
                      color: '#666',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text} 
                    primaryTypographyProps={{
                      fontSize: '0.9375rem',
                      fontWeight: location.pathname === item.path ? 600 : 400,
                      color: '#1a1a1a',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default Navbar; 