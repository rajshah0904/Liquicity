import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper,
  IconButton,
  InputAdornment,
  CircularProgress,
  Alert,
  Link
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Icons
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

// Custom components
import { 
  FloatingCard, 
  GradientText, 
  GradientBorder,
  AnimatedBackground
} from '../components/ui/ModernUIComponents';

const LoginContainer = styled(Container)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  position: 'relative',
  zIndex: 1,
}));

const LogoContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  marginBottom: theme.spacing(6),
  textAlign: 'center',
}));

const LogoIcon = styled(Box)(({ theme }) => ({
  width: 60,
  height: 60,
  borderRadius: '50%',
  background: 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 100%)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(2),
  boxShadow: '0 0 15px rgba(255,255,255,0.2)',
}));

const TextField_Styled = styled(TextField)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  '& .MuiOutlinedInput-root': {
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    borderRadius: theme.shape.borderRadius,
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.1)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.2)',
    },
    '&.Mui-focused fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.5)',
    },
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  '& .MuiInputBase-input': {
    color: '#FFFFFF',
  },
  '& .MuiInputAdornment-root': {
    color: 'rgba(255, 255, 255, 0.7)',
  },
}));

const LoginButton = styled(Button)(({ theme }) => ({
  background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  color: '#FFFFFF',
  marginTop: theme.spacing(2),
  padding: theme.spacing(1.2, 0),
  borderRadius: theme.shape.borderRadius,
  textTransform: 'none',
  fontWeight: 600,
  letterSpacing: '0.5px',
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'linear-gradient(90deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.25) 100%)',
    boxShadow: '0 0 15px rgba(255, 255, 255, 0.1)',
    transform: 'translateY(-2px)',
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
    transition: 'all 0.5s ease',
  },
  '&:hover::before': {
    left: '100%',
  },
}));

const FloatingGlassCard = styled(Paper)(({ theme }) => ({
  background: 'rgba(18, 18, 18, 0.5)',
  backdropFilter: 'blur(10px)',
  borderRadius: theme.shape.borderRadius * 2,
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  padding: theme.spacing(4),
  position: 'relative',
  overflow: 'hidden',
  width: '100%',
  maxWidth: 420,
}));

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { 
      duration: 0.6,
      ease: [0.22, 1, 0.36, 1] 
    } 
  }
};

const titleVariants = {
  hidden: { opacity: 0, y: -20 },
  visible: { 
    opacity: 1,
    y: 0,
    transition: { 
      delay: 0.2,
      duration: 0.5
    }
  }
};

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Validate inputs
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }
    
    setError('');
    setLoading(true);
    
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid username or password. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <>
      <AnimatedBackground />
      
      <LoginContainer maxWidth="sm">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={titleVariants}
        >
          <LogoContainer>
            <LogoIcon>
              <LockOutlinedIcon fontSize="large" sx={{ color: 'white' }} />
            </LogoIcon>
            <GradientText variant="h4" gutterBottom>
              Welcome to TerraFlow
            </GradientText>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 400 }}>
              The future of global money movement. Fast, secure, and borderless.
            </Typography>
          </LogoContainer>
        </motion.div>
        
        <motion.div
          initial="hidden"
          animate="visible"
          variants={cardVariants}
        >
          <GradientBorder>
            <FloatingGlassCard elevation={0}>
              <Typography variant="h5" align="center" gutterBottom>
                Sign In
              </Typography>
              
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}
              
              <form onSubmit={handleLogin}>
                <TextField_Styled
                  fullWidth
                  label="Username"
                  variant="outlined"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <AccountCircleOutlinedIcon />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField_Styled
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  variant="outlined"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LockOutlinedIcon />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          size="small"
                          sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                
                <LoginButton 
                  fullWidth 
                  type="submit"
                  disabled={loading}
                  size="large"
                >
                  {loading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
                </LoginButton>
                
                <Box sx={{ mt: 3, textAlign: 'center' }}>
                  <Link 
                    href="#" 
                    underline="hover" 
                    color="text.secondary"
                    sx={{ 
                      fontSize: '0.875rem',
                      transition: 'color 0.3s ease',
                      '&:hover': {
                        color: 'primary.main',
                      }
                    }}
                  >
                    Forgot password?
                  </Link>
                </Box>
                
                <Box sx={{ mt: 4, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Don't have an account?{' '}
                    <Link 
                      href="#" 
                      underline="hover" 
                      sx={{ 
                        color: 'primary.main',
                        fontWeight: 500,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          textShadow: '0 0 10px rgba(255,255,255,0.3)',
                        }
                      }}
                    >
                      Sign Up
                    </Link>
                  </Typography>
                </Box>
              </form>
            </FloatingGlassCard>
          </GradientBorder>
        </motion.div>
      </LoginContainer>
    </>
  );
};

export default Login; 