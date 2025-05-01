import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Button,
  Avatar,
  Menu,
  MenuItem,
  Collapse,
  Badge,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  AccountBalanceWallet,
  Send,
  Paid,
  ChatBubbleOutline,
  Assessment,
  Settings,
  Logout,
  AccountCircle,
  SwapHoriz,
  ExpandLess,
  ExpandMore,
  Payment,
  Receipt,
  Notifications,
  DarkMode
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const drawerWidth = 240;

const menuItems = [
  { text: 'Home', icon: <Dashboard />, path: '/dashboard' },
  { text: 'Wallet', icon: <AccountBalanceWallet />, path: '/wallets' },
  { text: 'Send & Receive', icon: <Send />, path: '/send' },
  { text: 'Transactions', icon: <Paid />, path: '/transactions' },
  { text: 'Swap Currency', icon: <SwapHoriz />, path: '/swap' }
];

const Layout = ({ children }) => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [notificationsAnchorEl, setNotificationsAnchorEl] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Auto-expand payment submenu if we're on a payment page
    if (location.pathname.includes('/payment') || location.pathname.includes('/invoice')) {
      setPaymentOpen(true);
    }
  }, [location.pathname]);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationsOpen = (event) => {
    setNotificationsAnchorEl(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/login');
  };

  const handleProfile = () => {
    handleMenuClose();
    navigate('/settings');
  };

  const handlePaymentToggle = () => {
    setPaymentOpen(!paymentOpen);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    // In a real app, you would implement theme switching here
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
          Liquicity
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (mobileOpen) handleDrawerToggle();
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
        
        {/* Payment submenu */}
        <ListItem disablePadding>
          <ListItemButton onClick={handlePaymentToggle}>
            <ListItemIcon>
              <Payment />
            </ListItemIcon>
            <ListItemText primary="Payments" />
            {paymentOpen ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
        </ListItem>
        <Collapse in={paymentOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            <ListItemButton 
              selected={location.pathname === '/payment/request'}
              onClick={() => {
                navigate('/payment/request');
                if (mobileOpen) handleDrawerToggle();
              }}
              sx={{ pl: 4 }}
            >
              <ListItemIcon>
                <Receipt fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Request Money" />
            </ListItemButton>
            <ListItemButton 
              selected={location.pathname === '/payment/invoices'}
              onClick={() => {
                navigate('/payment/invoices');
                if (mobileOpen) handleDrawerToggle();
              }}
              sx={{ pl: 4 }}
            >
              <ListItemIcon>
                <Receipt fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Invoices" />
            </ListItemButton>
          </List>
        </Collapse>

        <ListItem disablePadding>
          <ListItemButton 
            selected={location.pathname === '/settings'}
            onClick={() => {
              navigate('/settings');
              if (mobileOpen) handleDrawerToggle();
            }}
          >
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
        
        <ListItem disablePadding>
          <ListItemButton 
            selected={location.pathname === '/help'}
            onClick={() => {
              navigate('/help');
              if (mobileOpen) handleDrawerToggle();
            }}
          >
            <ListItemIcon>
              <ChatBubbleOutline />
            </ListItemIcon>
            <ListItemText primary="Help & Support" />
          </ListItemButton>
        </ListItem>
      </List>
      
      <Box sx={{ position: 'absolute', bottom: 0, width: '100%', p: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={darkMode}
              onChange={handleDarkModeToggle}
              name="darkMode"
              color="primary"
            />
          }
          label={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DarkMode fontSize="small" sx={{ mr: 1 }} />
              <Typography variant="body2">Dark Mode</Typography>
            </Box>
          }
        />
      </Box>
    </div>
  );

  // Use display names or initials for the avatar
  const getAvatarText = () => {
    if (currentUser) {
      if (currentUser.first_name && currentUser.last_name) {
        return `${currentUser.first_name.charAt(0)}${currentUser.last_name.charAt(0)}`;
      } else if (currentUser.username) {
        return currentUser.username.charAt(0).toUpperCase();
      }
    }
    return 'U';
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find(item => item.path === location.pathname)?.text || 
             'Liquicity'}
          </Typography>
          
          {currentUser ? (
            <>
              <IconButton 
                color="inherit"
                onClick={handleNotificationsOpen}
                sx={{ mr: 2 }}
              >
                <Badge badgeContent={3} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
              <Menu
                id="notifications-menu"
                anchorEl={notificationsAnchorEl}
                open={Boolean(notificationsAnchorEl)}
                onClose={handleNotificationsClose}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
              >
                <MenuItem onClick={handleNotificationsClose}>
                  <Typography variant="body2">You received $250.00 from John D.</Typography>
                </MenuItem>
                <MenuItem onClick={handleNotificationsClose}>
                  <Typography variant="body2">Your invoice #INV-2023 was paid</Typography>
                </MenuItem>
                <MenuItem onClick={handleNotificationsClose}>
                  <Typography variant="body2">Welcome to Liquicity!</Typography>
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => {
                  handleNotificationsClose();
                  navigate('/notifications');
                }}>
                  <Typography variant="body2" color="primary">View all notifications</Typography>
                </MenuItem>
              </Menu>
              
              <IconButton
                onClick={handleMenuOpen}
                color="inherit"
                edge="end"
                aria-label="account menu"
                aria-controls="menu-appbar"
                aria-haspopup="true"
              >
                <Avatar sx={{ bgcolor: 'secondary.main' }}>
                  {getAvatarText()}
                </Avatar>
              </IconButton>
              <Menu
                id="menu-appbar"
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
              >
                <MenuItem onClick={handleProfile}>
                  <ListItemIcon>
                    <AccountCircle fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Profile</ListItemText>
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <Logout fontSize="small" />
                  </ListItemIcon>
                  <ListItemText>Logout</ListItemText>
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Button color="inherit" onClick={() => navigate('/login')}>Login</Button>
          )}
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="navigation drawer"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: darkMode ? '#121212' : '#f5f5f5',
          color: darkMode ? '#fff' : 'inherit',
        }}
      >
        <Toolbar /> {/* Spacing to account for the AppBar */}
        {children || <Outlet />}
      </Box>
    </Box>
  );
};

export default Layout; 