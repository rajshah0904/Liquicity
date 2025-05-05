import React, { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, useMediaQuery, useTheme, Typography } from '@mui/material';
import { useAuth0 } from '@auth0/auth0-react';
import AuthFlow from './components/AuthFlow';
import KycForm from './components/KycForm';
import './App.css';

// Pages
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import Register from './pages/Register';
import VerifyEmail from './pages/VerifyEmail';
import PageDashboard from './pages/Dashboard';
import ModernCardDemo from './pages/ModernCardDemo';
import Wallet from './pages/Wallet';
import SendMoney from './pages/SendMoney';
import ReceiveMoney from './pages/ReceiveMoney';
import Transactions from './pages/Transactions';
import DepositFunds from './pages/DepositFunds';
import WithdrawFunds from './pages/WithdrawFunds';
import LandingPage from './pages/LandingPage';
import HowItWorks from './pages/HowItWorks';
import Security from './pages/Security';
import KYCVerification from './pages/KYCVerification';
import VerificationPending from './pages/VerificationPending';
import AuthCallback from './pages/AuthCallback';
import ProfilePage from './pages/Profile';

// Components
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import AnimatedBackground from './components/animations/AnimatedBackground';
import { AuthenticationGuard } from './components/auth/AuthenticationGuard';

// Providers
import { CustomThemeProvider as ThemeProvider } from './context/ThemeContext';

// Constants
const DRAWER_WIDTH = 260;

function App() {
  const { loginWithRedirect, logout, isAuthenticated, user, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <ThemeProvider>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <Typography variant="h5">Loading Liquicity application...</Typography>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <Routes>
        {/* Public Routes - No Authentication Required */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/register" element={<Register />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/security" element={<Security />} />
        <Route path="/callback" element={<AuthCallback />} />
        
        {/* Auth0 Flow Routes - Protected */}
        <Route path="/auth" element={<ProtectedRoute><AuthFlow /></ProtectedRoute>} />
        <Route path="/kyc" element={<ProtectedRoute><KycForm /></ProtectedRoute>} />
        <Route path="/verify-email" element={<ProtectedRoute><VerifyEmail /></ProtectedRoute>} />
        <Route path="/kyc-verification" element={<ProtectedRoute><KYCVerification /></ProtectedRoute>} />
        <Route path="/verification-pending" element={<ProtectedRoute><VerificationPending /></ProtectedRoute>} />
        
        {/* Dashboard Routes - Protected with Authenticated Layout */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <PageDashboard />
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
        <Route path="/profile" element={<AuthenticationGuard component={ProfilePage} />} />
      </Routes>
    </ThemeProvider>
  );
}

// Layouts
function AuthenticatedLayout({ children }) {
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAuth0();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);

  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  // Redirect to login if no user
  if (!isAuthenticated) {
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