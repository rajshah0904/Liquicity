import React, { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import { useAuth } from './context/AuthContext';

// Pages
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import Register from './pages/Register';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import ModernCardDemo from './pages/ModernCardDemo';
import Wallet from './pages/Wallet';
import SendMoney from './pages/SendMoney';
import ReceiveMoney from './pages/ReceiveMoney';
import Transactions from './pages/Transactions';
import DepositFunds from './pages/DepositFunds';
import WithdrawFunds from './pages/WithdrawFunds';

// Components
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import AnimatedBackground from './components/animations/AnimatedBackground';

// Providers
import { CustomThemeProvider as ThemeProvider } from './context/ThemeContext';

// Constants
const DRAWER_WIDTH = 260;

function App() {
  // Define routes that should use authenticated layout
  const authenticatedRoutes = [
    '/dashboard',
    '/wallet',
    '/send',
    '/receive',
    '/transactions',
    '/profile',
    '/settings',
  ];

  return (
    <ThemeProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />
        
        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <Dashboard />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/wallet"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <Wallet />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/send"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <SendMoney />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/receive"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <ReceiveMoney />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/transactions"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <Transactions />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/deposit"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <DepositFunds />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/withdraw"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <WithdrawFunds />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
        
        {/* Demo Route */}
        <Route
          path="/demo"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <ModernCardDemo />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </ThemeProvider>
  );
}

// Layouts
function AuthenticatedLayout({ children }) {
  const location = useLocation();
  const { currentUser } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);

  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  // Redirect to login if no user
  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Box sx={{ 
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      bgcolor: 'background.default'
    }}>
      <Navbar onDrawerToggle={handleDrawerToggle} drawerOpen={drawerOpen} showMenuIcon={isMobile} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: { xs: 8, md: 9 }, // Increased top padding to account for AppBar
          pb: { xs: 6, md: 8 },
          overflow: 'hidden',
          ml: { sm: drawerOpen ? `${DRAWER_WIDTH}px` : 0 }, // Add margin if drawer is open on non-mobile
          transition: 'margin-left 0.3s ease',
          width: { sm: drawerOpen ? `calc(100% - ${DRAWER_WIDTH}px)` : '100%' }, // Adjust width for non-mobile
        }}
      >
        <AnimatedBackground />
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}

export default App; 