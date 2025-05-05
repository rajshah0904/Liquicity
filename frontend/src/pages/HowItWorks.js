import React, { useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Grid,
  Typography,
  Link,
  Card,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ScrollHeader from '../components/ScrollHeader';

const HowItWorks = () => {
  const navigate = useNavigate();
  
  // Animation on scroll effect
  useEffect(() => {
    // Add animation styles to the document
    const style = document.createElement('style');
    style.innerHTML = `
      @keyframes fadeSlideIn {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .liquicity-animate-element {
        opacity: 0;
      }
      
      .liquicity-animate-element.liquicity-animated {
        animation: fadeSlideIn 0.2s ease-out forwards;
      }
      
      /* Add animation delay for consecutive items (faster) */
      .liquicity-animate-element:nth-child(1) {
        animation-delay: 0s;
      }
      
      .liquicity-animate-element:nth-child(2) {
        animation-delay: 0.03s;
      }
      
      .liquicity-animate-element:nth-child(3) {
        animation-delay: 0.06s;
      }
      
      .liquicity-animate-element:nth-child(4) {
        animation-delay: 0.09s;
      }
    `;
    document.head.appendChild(style);
    
    // Convert existing animate-on-scroll elements to use our new class
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      el.classList.add('liquicity-animate-element');
    });
    
    const handleScroll = () => {
      const elements = document.querySelectorAll('.liquicity-animate-element');
      elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight - 100;
        if (isVisible) {
          el.classList.add('liquicity-animated');
        }
      });
    };
    
    window.addEventListener('scroll', handleScroll);
    
    // Forcefully run animation on page load (important)
    const runInitialAnimations = () => {
      // Immediately add the animated class to all elements without checking visibility
      const elements = document.querySelectorAll('.liquicity-animate-element');
      elements.forEach(el => {
        el.classList.add('liquicity-animated');
      });
    };
    
    // Make sure animations run on initial load
    if (document.readyState === 'complete') {
      runInitialAnimations();
      // Also run after a slight delay to catch any race conditions
      setTimeout(runInitialAnimations, 50);
    } else {
      window.addEventListener('load', runInitialAnimations);
      // Also run after the load event with a slight delay
      window.addEventListener('load', () => setTimeout(runInitialAnimations, 50));
    }
    
    // Also trigger when window is resized
    window.addEventListener('resize', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleScroll);
      window.removeEventListener('load', runInitialAnimations);
      // Clean up the style when unmounting
      if (document.head.contains(style)) {
        document.head.removeChild(style);
      }
    };
  }, []);
  
  return (
    <Box sx={{
      minHeight: '100vh',
      backgroundColor: '#000000',
      color: '#fff',
      overflow: 'hidden',
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
              fontSize: { xs: '2.5rem', sm: '3.5rem', md: '4rem' },
              fontWeight: 800, 
              mb: 3,
              lineHeight: 1.1,
              letterSpacing: '-1px',
            }}
          >
            How Liquicity Works
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
            The digital wallet designed for everyone. Send money globally in minutes, not days, with better rates and lower fees.
          </Typography>
        </Container>
      </Box>
      
      {/* Process Flow Section */}
      <Box sx={{ py: { xs: 6, md: 10 } }}>
        <Container maxWidth="lg">
          <Typography variant="h3" className="liquicity-animate-element" sx={{ textAlign: 'center', mb: 8, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}>
            Sending Money Globally in Four Simple Steps
          </Typography>
          
          <Grid container spacing={6}>
            <Grid item xs={12} md={6} lg={3} className="liquicity-animate-element">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Typography variant="h1" sx={{ color: 'rgba(255,255,255,0.2)', mb: 2, fontWeight: 700 }}>1</Typography>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Load Your Wallet
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
                  Simply add funds to your Liquicity wallet from your bank account, debit card, or other payment methods.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3} className="liquicity-animate-element">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Typography variant="h1" sx={{ color: 'rgba(255,255,255,0.2)', mb: 2, fontWeight: 700 }}>2</Typography>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Select Recipient
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
                  Choose any Liquicity user you want to send money to.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3} className="liquicity-animate-element">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Typography variant="h1" sx={{ color: 'rgba(255,255,255,0.2)', mb: 2, fontWeight: 700 }}>3</Typography>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Confirm Transfer
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
                  Preview the exchange rate and fee, then confirm your transfer with just a tap.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3} className="liquicity-animate-element">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Typography variant="h1" sx={{ color: 'rgba(255,255,255,0.2)', mb: 2, fontWeight: 700 }}>4</Typography>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  Money Arrives
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
                  The recipient gets the money in minutes, not days. You'll both be notified when the transfer completes.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* Stablecoin Section */}
      <Box sx={{ 
        py: { xs: 8, md: 16 }, 
        backgroundColor: 'rgba(10, 10, 10, 0.8)',
        borderTop: '1px solid rgba(255,255,255,0.05)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}>
        <Container maxWidth="lg">
          <Grid container spacing={10} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h3" className="liquicity-animate-element" sx={{ mb: 4, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}>
                The Technology Behind Liquicity
              </Typography>
              <Typography variant="body1" className="liquicity-animate-element" sx={{ mb: 4, color: 'rgba(255,255,255,0.7)', lineHeight: 1.7 }}>
                Liquicity uses stablecoins — digital currencies designed to maintain a stable value — to make cross-border payments faster and cheaper than traditional banking.
              </Typography>
              <Typography variant="body1" className="liquicity-animate-element" sx={{ mb: 6, color: 'rgba(255,255,255,0.7)', lineHeight: 1.7 }}>
                When you send money, we convert it to stablecoins for the transfer and then back to the recipient's local currency. All this happens behind the scenes — you don't need to understand the technology to use it.
              </Typography>
              
              <Box sx={{ 
                p: 4, 
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
              }} className="liquicity-animate-element">
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                  Benefits for You
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={6} className="liquicity-animate-element">
                    <Typography variant="body2" paragraph sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      • Instant transfers
                    </Typography>
                    <Typography variant="body2" paragraph sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      • Lower fees
                    </Typography>
                    <Typography variant="body2" paragraph sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      • Available 24/7
                    </Typography>
                  </Grid>
                  <Grid item xs={6} className="liquicity-animate-element">
                    <Typography variant="body2" paragraph sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      • Better exchange rates
                    </Typography>
                    <Typography variant="body2" paragraph sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      • Full transparency
                    </Typography>
                    <Typography variant="body2" paragraph sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      • No hidden charges
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ 
                width: '100%',
                height: { xs: '300px', md: '450px' },
                borderRadius: '10px',
                overflow: 'hidden',
                background: 'linear-gradient(135deg, rgba(25,118,210,0.2) 0%, rgba(32,43,96,0.3) 100%)',
                border: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
              }}>
                <Box sx={{
                  width: '70%',
                  height: '70%',
                  borderRadius: '50%',
                  position: 'absolute',
                  background: 'radial-gradient(circle, rgba(25,118,210,0.4) 0%, rgba(25,118,210,0.1) 70%, rgba(25,118,210,0) 100%)',
                }}/>
                <Typography variant="h2" sx={{ 
                  fontWeight: 800, 
                  color: 'rgba(255,255,255,0.9)',
                  textShadow: '0 0 20px rgba(0,112,243,0.5)',
                  zIndex: 1,
                  fontSize: { xs: '3rem', md: '5rem' }
                }}>
                  USDC
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* Wallet Features */}
      <Box sx={{ py: { xs: 8, md: 14 } }}>
        <Container maxWidth="lg">
          <Typography variant="h3" className="liquicity-animate-element" sx={{ textAlign: 'center', mb: 8, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}>
            Your Liquicity Wallet Features
          </Typography>
          
          <Grid container spacing={6} justifyContent="center">
            <Grid item xs={12} md={6} className="liquicity-animate-element">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  For Individuals
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
                  Send money to family abroad, pay for services internationally, or spend while traveling — all with competitive rates.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="liquicity-animate-element">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                  For Small Businesses
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6 }}>
                  Pay international suppliers, receive payments from global customers, and manage your business finances all in one place.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* CTA Section */}
      <Box sx={{ 
        py: { xs: 10, md: 16 },
        backgroundImage: 'linear-gradient(to right, rgba(25, 25, 25, 0.9), rgba(35, 35, 35, 0.9))',
        borderTop: '1px solid rgba(255,255,255,0.1)',
      }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h3" className="liquicity-animate-element" sx={{ mb: 3, fontWeight: 700 }}>
            Ready to Get Started?
          </Typography>
          <Typography variant="body1" className="liquicity-animate-element" sx={{ mb: 5, color: 'rgba(255,255,255,0.7)', maxWidth: '600px', mx: 'auto' }}>
            Join thousands of others who are already saving money on international transfers with Liquicity.
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4 }} className="liquicity-animate-element">
            <Button 
              variant="contained" 
              size="large"
              endIcon={<ArrowForwardIcon />}
              onClick={() => { navigate('/'); window.scrollTo(0, 0); }}
              sx={{ 
                py: 1.8, 
                px: 5, 
                borderRadius: '6px',
                background: '#0070f3',
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 500,
                '&:hover': { background: '#0060df' },
              }}
            >
              Join Waitlist
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default HowItWorks; 