import React, { useState, useEffect } from 'react';
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
  Divider,
  Tooltip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth0 } from '@auth0/auth0-react';
import LoginButton, { SignupButton } from './auth/Login';
import LogoutButton from './auth/Logout';

// Icons
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import SendIcon from '@mui/icons-material/Send';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import SettingsIcon from '@mui/icons-material/Settings';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import PersonIcon from '@mui/icons-material/Person';
import CodeIcon from '@mui/icons-material/Code';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import QrCodeIcon from '@mui/icons-material/QrCode';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import CurrencyBitcoinIcon from '@mui/icons-material/CurrencyBitcoin';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import CreditCardIcon from '@mui/icons-material/CreditCard';

import { 
  GlassIconButton, 
  GlowingText,
  GradientText
} from './ui/ModernUIComponents';

import LogoSVG from './LogoSVG';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  background: '#000000',
  backdropFilter: 'blur(10px)',
  borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  boxShadow: 'none',
}));

const Logo = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  cursor: 'pointer',
}));

const LogoIcon = styled('div')(({ theme }) => ({
  width: 32,
  height: 32,
  borderRadius: 0,
  background: '#000000',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const UserInfo = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(0.5, 1),
  borderRadius: 0,
  background: '#000000',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
  },
}));

const StyledAvatar = styled(Avatar)(({ theme }) => ({
  width: 32,
  height: 32,
  borderRadius: 0,
  border: '1px solid rgba(255, 255, 255, 0.2)',
  background: '#000000',
  color: '#FFFFFF',
}));

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  '& .MuiDrawer-paper': {
    width: 260,
    background: '#000000',
    backdropFilter: 'blur(20px)',
    borderRight: '1px solid rgba(255, 255, 255, 0.05)',
    padding: theme.spacing(2, 0),
  },
}));

const DrawerHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const NavItem = styled(ListItem)(({ theme, active }) => ({
  borderRadius: 0,
  margin: theme.spacing(0.5, 2),
  background: active ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
  transition: 'all 0.2s ease',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
  },
}));

const NavDivider = styled(Divider)(({ theme }) => ({
  margin: theme.spacing(2, 2),
  background: 'linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 100%)',
}));

const navItems = [
  { path: '/dashboard', icon: <DashboardIcon />, text: 'Dashboard' },
  { path: '/wallet', icon: <AccountBalanceWalletIcon />, text: 'Wallet' },
  { path: '/payments/send', icon: <SendIcon />, text: 'Send' },
  { path: '/payments/request', icon: <QrCodeIcon />, text: 'Receive' },
  { path: '/card', icon: <CreditCardIcon />, text: 'Card' },
  { path: '/transactions', icon: <ReceiptLongIcon />, text: 'Transactions' },
];

const navItemsBottom = [
  { path: '/profile', icon: <AccountCircleIcon />, text: 'Profile' },
  { path: '/settings', icon: <SettingsIcon />, text: 'Settings' },
  { path: '/logout', icon: <ExitToAppIcon />, text: 'Logout' },
];

const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } }
};

const fadeInUp = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } }
};

const Navbar = ({ onDrawerToggle, drawerOpen, showMenuIcon = false }) => {
  // If drawerOpen prop is not provided, use local state
  const [localDrawerOpen, setLocalDrawerOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated, user, isLoading, logout } = useAuth0();

  // Use either prop or local state depending on what's provided
  const isDrawerOpen = drawerOpen !== undefined ? drawerOpen : localDrawerOpen;

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

  const isActive = (path) => {
    return location.pathname === path;
  };

  const drawer = (
    <>
      <DrawerHeader>
        <Logo>
          <LogoSVG size={120} />
        </Logo>
      </DrawerHeader>
      
      <Box sx={{ mt: 2 }}>
        <List component="nav">
          {navItems.map((item, index) => (
            <motion.div
              key={item.text}
              initial="hidden"
              animate="visible"
              variants={fadeInUp}
              transition={{ delay: 0.1 * index }}
            >
              <NavItem 
                button 
                active={isActive(item.path) ? 1 : 0} 
                onClick={() => handleNavigation(item.path)}
              >
                <ListItemIcon sx={{ minWidth: 40, color: isActive(item.path) ? 'primary.main' : 'text.secondary' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  primaryTypographyProps={{ 
                    color: isActive(item.path) ? 'primary.main' : 'text.primary',
                    fontWeight: isActive(item.path) ? 600 : 400,
                  }} 
                />
              </NavItem>
            </motion.div>
          ))}
        </List>
      </Box>
      
      <NavDivider />
      
      <Box sx={{ mt: 1 }}>
        <List component="nav">
          {navItemsBottom.map((item, index) => (
            <motion.div
              key={item.text}
              initial="hidden"
              animate="visible"
              variants={fadeInUp}
              transition={{ delay: 0.5 + (0.1 * index) }}
            >
              <NavItem 
                button 
                active={isActive(item.path) ? 1 : 0} 
                onClick={() => handleNavigation(item.path)}
              >
                <ListItemIcon sx={{ minWidth: 40, color: isActive(item.path) ? 'primary.main' : 'text.secondary' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{ 
                    color: isActive(item.path) ? 'primary.main' : 'text.primary',
                    fontWeight: isActive(item.path) ? 600 : 400,
                  }}  
                />
              </NavItem>
            </motion.div>
          ))}
        </List>
      </Box>
    </>
  );

  return (
    <>
      <AppBar 
        position="fixed" 
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          boxShadow: 'none',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          backgroundColor: '#000000'
        }}
      >
        <Toolbar>
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
          
          <Box onClick={() => navigate('/')} sx={{ 
            display: 'flex', 
            alignItems: 'center',
            cursor: 'pointer',
            gap: 1
          }}>
            <LogoSVG size={32} />
            <Typography variant="h6" noWrap component="div" sx={{ display: { xs: 'none', sm: 'block' } }}>
              Liquicity
            </Typography>
          </Box>
          
          <Box sx={{ flexGrow: 1 }} />
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {isLoading ? (
              <div className="auth-loading">Loading...</div>
            ) : isAuthenticated ? (
              <Box sx={{ position: 'relative' }}>
                <IconButton onClick={() => navigate('/profile')} sx={{ p: 0 }}>
                  {user?.picture ? (
                    <Avatar 
                      src={user.picture}
                      alt="Profile"
                      sx={{ 
                        width: 40, 
                        height: 40, 
                        cursor: 'pointer',
                        border: '2px solid rgba(255, 255, 255, 0.1)'
                      }}
                    />
                  ) : (
                    <Avatar 
                      sx={{ 
                        width: 40, 
                        height: 40, 
                        bgcolor: 'primary.main',
                        cursor: 'pointer',
                        border: '2px solid rgba(255, 255, 255, 0.1)'
                      }}
                    >
                      {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                    </Avatar>
                  )}
                </IconButton>
              </Box>
            ) : (
              <div className="auth-buttons">
                <LoginButton />
                <SignupButton />
              </div>
            )}
          </Box>
        </Toolbar>
      </AppBar>

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
            paddingTop: '64px', // Match the height of the AppBar to push content down
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(10px)',
            borderRight: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        <Box sx={{ overflow: 'auto', display: 'flex', flexDirection: 'column', height: '100%' }}>
          <List>
            {navItems.map((item) => (
              <ListItem 
                key={item.path} 
                disablePadding 
                sx={{ 
                  display: 'block',
                  mb: 0.5,
                }}
              >
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  selected={location.pathname === item.path}
                  sx={{
                    minHeight: 48,
                    justifyContent: 'initial',
                    px: 2.5,
                    borderRadius: 0,
                    transition: 'all 0.2s ease-in-out',
                    ...(location.pathname === item.path && {
                      borderLeft: (theme) => 
                        `4px solid ${theme.palette.primary.main}`,
                      backgroundColor: (theme) => 
                        theme.palette.mode === 'dark' 
                          ? 'rgba(255, 255, 255, 0.1)' 
                          : 'rgba(0, 0, 0, 0.05)',
                    }),
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: 2,
                      justifyContent: 'center',
                      color: (theme) => 
                        location.pathname === item.path
                          ? theme.palette.primary.main
                          : theme.palette.text.secondary,
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text} 
                    primaryTypographyProps={{
                      fontWeight: location.pathname === item.path ? 'bold' : 'regular',
                      color: (theme) => 
                        location.pathname === item.path
                          ? theme.palette.text.primary
                          : theme.palette.text.secondary,
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          
          <Box sx={{ flexGrow: 1 }} />
          
          <List>
            {navItemsBottom.map((item) => (
              <ListItem 
                key={item.path} 
                disablePadding 
                sx={{ 
                  display: 'block',
                  mb: 0.5,
                }}
              >
                <ListItemButton
                  onClick={() => item.path === '/logout' ? handleLogout() : handleNavigation(item.path)}
                  selected={location.pathname === item.path}
                  sx={{
                    minHeight: 48,
                    justifyContent: 'initial',
                    px: 2.5,
                    borderRadius: 0,
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: 2,
                      justifyContent: 'center',
                      color: (theme) => 
                        location.pathname === item.path
                          ? theme.palette.primary.main
                          : theme.palette.text.secondary,
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text}
                    primaryTypographyProps={{
                      color: (theme) => 
                        location.pathname === item.path
                          ? theme.palette.text.primary
                          : theme.palette.text.secondary,
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