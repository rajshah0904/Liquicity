import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Button,
  Container,
  Grid,
  Typography,
  Link,
  useTheme,
  TextField,
  Snackbar,
  Alert,
} from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SendIcon from '@mui/icons-material/Send';
import ScrollHeader from '../components/ScrollHeader';

// Company logos as components
const GeicoLogo = () => (
  <img 
    src="/images/geico.png" 
    alt="GEICO" 
    style={{ 
      width: '180px', 
      height: 'auto',
      maxHeight: '50px',
      objectFit: 'contain'
    }} 
  />
);

const JPMorganLogo = () => (
  <img 
    src="/images/jp-morgan.png" 
    alt="JP Morgan" 
    style={{ 
      width: '600px', 
      height: 'auto',
      maxHeight: '150px',
      objectFit: 'contain'
    }} 
  />
);

const HarvardLogo = () => (
  <img 
    src="/images/harvard.png" 
    alt="Harvard Business School" 
    style={{ 
      width: '200px', 
      height: 'auto',
      maxHeight: '50px',
      objectFit: 'contain'
    }} 
  />
);

const LandingPage = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const staggerRefs = useRef([]);
  const [email, setEmail] = useState('');
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Animation on scroll effect
  useEffect(() => {
    const handleScroll = () => {
      const elements = document.querySelectorAll('.stagger-item');
      elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight - 100;
        if (isVisible) {
          el.classList.add('animated');
        }
      });
    };
    
    window.addEventListener('scroll', handleScroll);
    // Trigger once on load
    setTimeout(handleScroll, 300);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);
  
  const handleSubmitEmail = (e) => {
    e.preventDefault();
    
    // Basic email validation
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      console.error('Invalid email format');
      return;
    }
    
    setIsSubmitting(true);
    
    // Create FormData object for Google Forms submission
    const formData = new FormData();
    formData.append('entry.686220689', email); // Using the field ID
    
    // Submit to Google Form in the background
    fetch('https://docs.google.com/forms/d/1SROYG80T9o_XAAqNy0VmXK3MGPJJhz6G8yTqOSYmPho/formResponse', {
      method: 'POST',
      body: formData,
      mode: 'no-cors' // Important to avoid CORS issues
    })
    .then(() => {
      // Since we use no-cors, we won't get a proper response
      // but we can assume success and show the success message
      console.log('Email submitted:', email);
      setOpenSnackbar(true);
      setEmail('');
      setIsSubmitting(false);
    })
    .catch(error => {
      console.error('Error submitting to Google Form:', error);
      // Even if there's an error, show success to the user since
      // we can't get the actual error details due to no-cors
      setOpenSnackbar(true);
      setEmail('');
      setIsSubmitting(false);
    });
  };
  
  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };
  
  return (
    <Box sx={{
      minHeight: '100vh',
      backgroundColor: '#000000',
      color: '#fff',
      overflow: 'hidden',
      position: 'relative',
    }}>
      {/* Scrolling Header */}
      <ScrollHeader />

      {/* Hero Section with Dots Background */}
      <Box sx={{ 
        pt: { xs: 25, md: 30 },
        pb: { xs: 10, md: 20 },
        textAlign: 'center',
        position: 'relative',
        backgroundImage: 'radial-gradient(circle at 1px 1px, #333 1px, transparent 0)',
        backgroundSize: '40px 40px',
      }}>
        <Container maxWidth="md">
          <Typography 
            variant="h1" 
            className="fade-in"
            sx={{ 
              fontSize: { xs: '2.5rem', sm: '3.5rem', md: '4.5rem' },
              fontWeight: 800, 
              mb: 3,
              lineHeight: 1.1,
              letterSpacing: '-1px',
            }}
          >
            Revolutionizing Cross-Border Payments
          </Typography>
          
          <Typography 
            variant="h5"
            className="slide-up"
            sx={{ 
              mb: 6,
              fontWeight: 400,
              color: 'rgba(255,255,255,0.7)',
              fontSize: { xs: '1rem', sm: '1.2rem' },
              maxWidth: '700px',
              mx: 'auto',
              animationDelay: '0.2s',
            }}
          >
            Send money across borders faster, cheaper, and more securely than ever before.
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, mt: 6 }} className="scale-in">
            <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)' }}>
              Join our waitlist to get early access
            </Typography>
            
            <form onSubmit={handleSubmitEmail} style={{ width: '100%', maxWidth: '500px' }}>
              <Box sx={{ display: 'flex', gap: 1, width: '100%' }}>
                <TextField
                  variant="outlined"
                  placeholder="Enter your email address"
                  fullWidth
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  type="email"
                  disabled={isSubmitting}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: 'white',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.5)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#0070f3',
                      },
                    },
                    '& .MuiInputBase-input::placeholder': {
                      color: 'rgba(255, 255, 255, 0.5)',
                    },
                  }}
                />
                <Button 
                  variant="contained" 
                  type="submit"
                  className="button-glow"
                  endIcon={<SendIcon />}
                  disabled={isSubmitting}
                  sx={{ 
                    backgroundColor: '#0070f3',
                    color: '#fff',
                    borderRadius: '6px',
                    textTransform: 'none',
                    fontSize: '1rem',
                    px: 3,
                    '&:hover': { backgroundColor: '#0060df' }
                  }}
                >
                  {isSubmitting ? 'Joining...' : 'Join'}
                </Button>
              </Box>
            </form>
            
            <Button 
              variant="text" 
              endIcon={<ArrowForwardIcon />}
              sx={{ 
                color: 'rgba(255,255,255,0.7)', 
                textTransform: 'none',
                fontSize: '0.9rem',
                mt: 2,
                '&:hover': { color: '#fff', backgroundColor: 'transparent' }
              }}
            >
              Contact Us
            </Button>
          </Box>
          
          <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
            <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
              Thank you for joining our waitlist!
            </Alert>
          </Snackbar>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Box sx={{ py: { xs: 8, md: 16 } }}>
        <Container maxWidth="lg">
          <Typography 
            variant="h3" 
            className="stagger-item"
            sx={{ textAlign: 'center', mb: 8, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}
          >
            How It Works (Simply Put)
          </Typography>
          
          <Typography 
            variant="body1" 
            className="stagger-item"
            sx={{ mb: 6, maxWidth: '800px', mx: 'auto', textAlign: 'center', color: 'rgba(255,255,255,0.7)' }}
          >
            Sending money internationally can be slow and expensive, but with our platform, everything changes.
          </Typography>
          
          <Grid container spacing={6}>
            <Grid item xs={12} md={6} lg={3} className="stagger-item">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(30, 30, 30, 0.2)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-10px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  backgroundColor: 'rgba(40, 40, 40, 0.3)',
                }
              }}
              className="feature-card"
              >
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Send Money
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 3, lineHeight: 1.6 }}>
                  You send money from your local bank, just like any normal payment. No complex steps—just a regular bank transfer.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3} className="stagger-item">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(30, 30, 30, 0.2)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-10px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  backgroundColor: 'rgba(40, 40, 40, 0.3)',
                }
              }}
              className="feature-card"
              >
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Conversion
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 3, lineHeight: 1.6 }}>
                  The money gets converted into a stablecoin. This digital money keeps its value steady, ensuring no surprises with exchange rates.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3} className="stagger-item">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(30, 30, 30, 0.2)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-10px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  backgroundColor: 'rgba(40, 40, 40, 0.3)',
                }
              }}
              className="feature-card"
              >
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Send Globally
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 3, lineHeight: 1.6 }}>
                  The stablecoin moves across borders instantly, without going through multiple banks or waiting days.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3} className="stagger-item">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(30, 30, 30, 0.2)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-10px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  backgroundColor: 'rgba(40, 40, 40, 0.3)',
                }
              }}
              className="feature-card"
              >
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Receive Locally
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 3, lineHeight: 1.6 }}>
                  The recipient gets the money in their local currency. The whole process takes minutes, not days.
                </Typography>
              </Box>
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
            <Button 
              variant="outlined" 
              endIcon={<ArrowForwardIcon />} 
              size="large"
              onClick={() => navigate('/how-it-works')}
              className="stagger-item"
              sx={{ 
                borderColor: 'rgba(255,255,255,0.3)', 
                color: '#fff',
                borderRadius: '6px',
                textTransform: 'none',
                fontSize: '1rem',
                px: 4,
                py: 1.5,
                '&:hover': { borderColor: '#fff', backgroundColor: 'rgba(255, 255, 255, 0.05)' }
              }}
            >
              Learn more about how it works
            </Button>
          </Box>
        </Container>
      </Box>
      
      {/* Benefits Section */}
      <Box sx={{ 
        py: { xs: 8, md: 16 }, 
        backgroundColor: 'rgba(10, 10, 10, 0.8)',
        borderTop: '1px solid rgba(255,255,255,0.05)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}>
        <Container maxWidth="lg">
          <Typography 
            variant="h3" 
            className="stagger-item"
            sx={{ textAlign: 'center', mb: 8, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}
          >
            The Liquicity Advantage
          </Typography>
          
          <Grid container spacing={6}>
            <Grid item xs={12} md={6} className="stagger-item">
              <Box sx={{ 
                p: 5, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(20, 20, 20, 0.6)',
              }}
              className="feature-card"
              >
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
                  Speed & Efficiency
                </Typography>
                
                <Box sx={{ mb: 4 }}>
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Transfers complete in minutes, not days</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>No more waiting over weekends or holidays</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>24/7 availability for sending and receiving</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Perfect for urgent business needs or family emergencies</Box>
                  </Typography>
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="stagger-item">
              <Box sx={{ 
                p: 5, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(20, 20, 20, 0.6)',
              }}
              className="feature-card"
              >
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
                  Cost Savings
                </Typography>
                
                <Box sx={{ mb: 4 }}>
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Up to 80% cheaper than traditional banks</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>No hidden fees or surprising conversion rates</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Transparent pricing shown before you send</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Keep more of your hard-earned money</Box>
                  </Typography>
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="stagger-item">
              <Box sx={{ 
                p: 5, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(20, 20, 20, 0.6)',
              }}
              className="feature-card"
              >
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
                  Security & Compliance
                </Typography>
                
                <Box sx={{ mb: 4 }}>
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Bank-level security for your financial data</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Fully regulated in all operating jurisdictions</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Advanced fraud prevention systems</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Comprehensive KYC and AML procedures</Box>
                  </Typography>
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="stagger-item">
              <Box sx={{ 
                p: 5, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.05)',
                backgroundColor: 'rgba(20, 20, 20, 0.6)',
              }}
              className="feature-card"
              >
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
                  Ease of Use
                </Typography>
                
                <Box sx={{ mb: 4 }}>
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Simple, intuitive user interface</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Send money with just a few clicks</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Real-time tracking of your transfers</Box>
                  </Typography>
                  
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Dedicated support available when you need it</Box>
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* Footer */}
      <Box sx={{ 
        py: 8,
        borderTop: '1px solid rgba(255,255,255,0.05)',
      }}>
        <Container maxWidth="lg">
          {/* Team Experience Section - Moved above footer links */}
          <Box sx={{ mb: 8, pb: 6, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.7)', textAlign: 'center', fontSize: '0.9rem' }}>
              Our team has worked at
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: { xs: 5, md: 10 }, justifyContent: 'center', alignItems: 'center' }}>
              <Box sx={{ opacity: 0.7, transition: 'opacity 0.3s', '&:hover': { opacity: 1 } }}>
                <GeicoLogo />
              </Box>
              <Box sx={{ opacity: 0.7, transition: 'opacity 0.3s', '&:hover': { opacity: 1 } }}>
                <JPMorganLogo />
              </Box>
              <Box sx={{ opacity: 0.7, transition: 'opacity 0.3s', '&:hover': { opacity: 1 } }}>
                <HarvardLogo />
              </Box>
            </Box>
          </Box>

          <Grid container spacing={6}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
                Liquicity
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 2 }}>
                Revolutionizing cross-border payments with stablecoin technology.
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                © 2025 Liquicity. All rights reserved.
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 3 }}>
                Quick Links
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                <RouterLink to="/" style={{ textDecoration: 'none', marginBottom: '0.75rem', color: 'inherit', opacity: 0.7 }}>Home</RouterLink>
                <RouterLink to="/how-it-works" style={{ textDecoration: 'none', marginBottom: '0.75rem', color: 'inherit', opacity: 0.7 }}>How it works</RouterLink>
                <RouterLink to="/security" style={{ textDecoration: 'none', color: 'inherit', opacity: 0.7 }}>Security</RouterLink>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 3 }}>
                Legal
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                <Link href="#" underline="none" color="inherit" sx={{ mb: 1.5, opacity: 0.7, '&:hover': { opacity: 1 } }}>Terms of Service</Link>
                <Link href="#" underline="none" color="inherit" sx={{ mb: 1.5, opacity: 0.7, '&:hover': { opacity: 1 } }}>Privacy Policy</Link>
                <Link href="#" underline="none" color="inherit" sx={{ opacity: 0.7, '&:hover': { opacity: 1 } }}>Compliance</Link>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage; 