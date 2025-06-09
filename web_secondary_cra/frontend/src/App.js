import React, { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, useMediaQuery, useTheme, Typography } from '@mui/material';
import { useAuth0 } from '@auth0/auth0-react';
import './App.css';
import theme from './theme';
import MockDataProvider from './components/MockDataProvider';

// Pages
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import PageDashboard from './pages/Dashboard';
import LandingPage from './pages/LandingPage';
import HowItWorks from './pages/HowItWorks';
import Security from './pages/Security';
import KYCVerification from './pages/KYCVerification';
import AuthCallback from './pages/AuthCallback';
import WalletPage from './pages/Wallet';
import DepositPage from './pages/wallet/Deposit';
import WithdrawPage from './pages/wallet/Withdraw';
import SendPage from './pages/payments/Send';
import RequestPage from './pages/payments/Request';
import TransactionsPage from './pages/Transactions';
import CardPage from './pages/Card';
import SettingsPage from './pages/Settings';
import ProfilePage from './pages/Profile';

// Components
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import AnimatedBackground from './components/animations/AnimatedBackground';
import { AuthenticationGuard } from './components/auth/AuthenticationGuard';
import KycGuard from './components/auth/KycGuard';
import RequireKyc from './components/auth/RequireKyc';

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
      <MockDataProvider>
      <Routes>
        {/* Public Routes - No Authentication Required */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/security" element={<Security />} />
        <Route path="/callback" element={<AuthCallback />} />
        
        {/* Auth0 Flow Routes - Protected */}
        <Route path="/kyc-verification" element={<ProtectedRoute><KycGuard><KYCVerification/></KycGuard></ProtectedRoute>} />
        
        {/* Dashboard Routes - Protected with Authenticated Layout */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <RequireKyc>
                <AuthenticatedLayout>
                  <PageDashboard />
                </AuthenticatedLayout>
              </RequireKyc>
            </ProtectedRoute>
          }
        />

        {/* Wallet Routes - Protected with Authenticated Layout */}
        <Route path="/wallet" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><WalletPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />
        <Route path="/wallet/deposit" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><DepositPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />
        <Route path="/wallet/withdraw" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><WithdrawPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />

        {/* Payments Routes - Protected with Authenticated Layout */}
        <Route path="/payments/send" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><SendPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />
        <Route path="/payments/request" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><RequestPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />

          {/* Card Route */}
          <Route path="/card" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><CardPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />

          {/* Settings & Profile */}
          <Route path="/settings" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><SettingsPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><ProfilePage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />

        {/* Transactions Routes - Protected with Authenticated Layout */}
        <Route path="/transactions" element={<ProtectedRoute><RequireKyc><AuthenticatedLayout><TransactionsPage/></AuthenticatedLayout></RequireKyc></ProtectedRoute>} />
      </Routes>
      </MockDataProvider>
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