import React, { useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Grid,
  Typography,
  Link,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SecurityIcon from '@mui/icons-material/Security';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import GavelIcon from '@mui/icons-material/Gavel';
import ShieldIcon from '@mui/icons-material/Shield';
import LockIcon from '@mui/icons-material/Lock';
import PrivacyTipIcon from '@mui/icons-material/PrivacyTip';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import DeviceUnknownIcon from '@mui/icons-material/DeviceUnknown';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import ScrollHeader from '../components/ScrollHeader';

const Security = () => {
  const navigate = useNavigate();
  
  // Animation on scroll effect
  useEffect(() => {
    const handleScroll = () => {
      const elements = document.querySelectorAll('.animate-on-scroll');
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
          <SecurityIcon sx={{ fontSize: '5rem', color: '#0070f3', mb: 3 }} className="fade-in animate-on-scroll" />
          <Typography 
            variant="h1" 
            className="fade-in animate-on-scroll"
            sx={{ 
              fontSize: { xs: '2.5rem', sm: '3.5rem', md: '4rem' },
              fontWeight: 800, 
              mb: 3,
              lineHeight: 1.1,
              letterSpacing: '-1px',
            }}
          >
            Your Money, Protected
          </Typography>
          
          <Typography 
            variant="h5"
            className="slide-up animate-on-scroll"
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
            We've built Liquicity with bank-grade security to protect your money and personal information at all times.
          </Typography>
        </Container>
      </Box>
      
      {/* Security Features */}
      <Box sx={{ py: { xs: 4, md: 10 } }}>
        <Container maxWidth="lg" sx={{ px: { xs: 3, md: 3 } }}>
          <Typography 
            variant="h3" 
            className="animate-on-scroll"
            sx={{ textAlign: 'center', mb: { xs: 5, md: 8 }, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}
          >
            How We Protect Your Account
          </Typography>
          
          <Grid container spacing={{ xs: 4, md: 8 }}>
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box sx={{ 
                p: { xs: 4, md: 5 },
                height: 'auto',
                minHeight: { xs: '180px', md: '200px' },
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                display: 'flex',
                flexDirection: 'column',
                mb: { xs: 0, md: 2 },
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ 
                    width: '48px', 
                    height: '48px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    color: '#0070f3',
                    mr: 2.5,
                    flexShrink: 0,
                    backgroundColor: 'rgba(0, 112, 243, 0.15)',
                    borderRadius: '8px',
                  }}>
                    <LockIcon sx={{ fontSize: '2rem' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 600, fontSize: { xs: '1.25rem', md: '1.5rem' } }}>
                    2-Factor Authentication
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6, mt: 1 }}>
                  Add an extra layer of security to your account with 2FA, making it difficult for unauthorized users to access your wallet.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box sx={{ 
                p: { xs: 4, md: 5 },
                height: 'auto',
                minHeight: { xs: '180px', md: '200px' },
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                display: 'flex',
                flexDirection: 'column',
                mb: { xs: 0, md: 2 },
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ 
                    width: '48px', 
                    height: '48px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    color: '#0070f3',
                    mr: 2.5,
                    flexShrink: 0,
                    backgroundColor: 'rgba(0, 112, 243, 0.15)',
                    borderRadius: '8px',
                  }}>
                    <DeviceUnknownIcon sx={{ fontSize: '2rem' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 600, fontSize: { xs: '1.25rem', md: '1.5rem' } }}>
                    Device Recognition
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6, mt: 1 }}>
                  We monitor logins from new devices and locations, alerting you immediately of any suspicious activity on your account.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box sx={{ 
                p: { xs: 4, md: 5 },
                height: 'auto',
                minHeight: { xs: '180px', md: '200px' },
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                display: 'flex',
                flexDirection: 'column',
                mb: { xs: 0, md: 2 },
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ 
                    width: '48px', 
                    height: '48px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    color: '#0070f3',
                    mr: 2.5,
                    flexShrink: 0,
                    backgroundColor: 'rgba(0, 112, 243, 0.15)',
                    borderRadius: '8px',
                  }}>
                    <AccountBalanceWalletIcon sx={{ fontSize: '2rem' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 600, fontSize: { xs: '1.25rem', md: '1.5rem' } }}>
                    Secure Transaction Limits
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6, mt: 1 }}>
                  Set daily and monthly transaction limits that work for you, keeping your account secure even if your credentials are compromised.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box sx={{ 
                p: { xs: 4, md: 5 },
                height: 'auto',
                minHeight: { xs: '180px', md: '200px' },
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                transition: 'all 0.3s ease',
                display: 'flex',
                flexDirection: 'column',
                mb: { xs: 0, md: 2 },
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ 
                    width: '48px', 
                    height: '48px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    color: '#0070f3',
                    mr: 2.5,
                    flexShrink: 0,
                    backgroundColor: 'rgba(0, 112, 243, 0.15)',
                    borderRadius: '8px',
                  }}>
                    <VerifiedUserIcon sx={{ fontSize: '2rem' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 600, fontSize: { xs: '1.25rem', md: '1.5rem' } }}>
                    Instant Alerts
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.6, mt: 1 }}>
                  Receive real-time notifications about all account activities, including transactions, logins, and account changes.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* KYC and AML Section */}
      <Box sx={{ 
        py: { xs: 6, md: 16 }, 
        backgroundColor: 'rgba(10, 10, 10, 0.8)',
        borderTop: '1px solid rgba(255,255,255,0.05)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}>
        <Container maxWidth="lg" sx={{ px: { xs: 3, md: 3 } }}>
          <Typography 
            variant="h3" 
            className="animate-on-scroll"
            sx={{ textAlign: 'center', mb: 10, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}
          >
            KYC & Anti-Money Laundering
          </Typography>
          
          <Grid container spacing={6}>
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box sx={{ 
                p: { xs: 4, md: 5 },
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
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                  <AssignmentTurnedInIcon sx={{ color: '#0070f3', fontSize: '2.5rem', mr: 3 }} />
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    Know Your Customer
                  </Typography>
                </Box>
                
                <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.8)', lineHeight: 1.7 }}>
                  Our KYC process is designed to verify your identity while keeping your information secure. This helps us:
                </Typography>
                
                <Box sx={{ pl: 2 }}>
                  <Typography variant="body1" className="animate-on-scroll" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Ensure you're the only person who can access your account and funds</Box>
                  </Typography>
                  
                  <Typography variant="body1" className="animate-on-scroll" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Comply with financial regulations in all countries where we operate</Box>
                  </Typography>
                  
                  <Typography variant="body1" className="animate-on-scroll" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Prevent identity theft and fraud that could affect you or other users</Box>
                  </Typography>
                  
                  <Typography variant="body1" className="animate-on-scroll" sx={{ color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Create a trusted community of verified users for safer transactions</Box>
                  </Typography>
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box sx={{ 
                p: { xs: 4, md: 5 },
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
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                  <AttachMoneyIcon sx={{ color: '#0070f3', fontSize: '2.5rem', mr: 3 }} />
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    Anti-Money Laundering
                  </Typography>
                </Box>
                
                <Typography variant="body1" sx={{ mb: 4, color: 'rgba(255,255,255,0.8)', lineHeight: 1.7 }}>
                  Our AML policies protect you and our platform from criminal activity. We implement:
                </Typography>
                
                <Box sx={{ pl: 2 }}>
                  <Typography variant="body1" className="animate-on-scroll" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Sophisticated transaction monitoring systems that flag unusual activity</Box>
                  </Typography>
                  
                  <Typography variant="body1" className="animate-on-scroll" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Risk-based assessment of transactions matching global AML standards</Box>
                  </Typography>
                  
                  <Typography variant="body1" className="animate-on-scroll" sx={{ mb: 2, color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Regular checks against global sanctions lists and PEP databases</Box>
                  </Typography>
                  
                  <Typography variant="body1" className="animate-on-scroll" sx={{ color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'flex-start' }}>
                    <Box component="span" sx={{ color: '#0070f3', mr: 2, fontSize: '1.5rem' }}>•</Box>
                    <Box>Compliance with BSA, FATF recommendations, and local AML laws worldwide</Box>
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* Regulatory Compliance */}
      <Box sx={{ py: { xs: 8, md: 14 } }}>
        <Container maxWidth="lg">
          <Typography variant="h3" className="animate-on-scroll" sx={{ textAlign: 'center', mb: 10, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}>
            Regulatory Compliance
          </Typography>
          
          <Grid container spacing={8} alignItems="center">
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box sx={{ 
                p: 6, 
                borderRadius: 3,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(25, 25, 25, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <GavelIcon sx={{ 
                  fontSize: { xs: '150px', md: '200px' }, 
                  color: 'rgba(255,255,255,0.1)',
                  filter: 'drop-shadow(0 0 20px rgba(0,112,243,0.3))',
                }} />
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} className="animate-on-scroll">
              <Box>
                <Typography variant="h4" className="animate-on-scroll" sx={{ fontWeight: 700, mb: 4 }}>
                  Compliant & Licensed
                </Typography>
                
                <Box sx={{ mb: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 4 }} className="animate-on-scroll">
                    <VerifiedUserIcon sx={{ color: '#0070f3', mr: 2, mt: 0.5, flexShrink: 0 }} />
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>Licensed Money Transmitter</Typography>
                      <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6 }}>
                        We are licensed in multiple jurisdictions to provide money transfer services, ensuring we meet the highest regulatory standards.
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 4 }} className="animate-on-scroll">
                    <VerifiedUserIcon sx={{ color: '#0070f3', mr: 2, mt: 0.5, flexShrink: 0 }} />
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>Regulatory Framework</Typography>
                      <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6 }}>
                        We comply with all relevant regulations including FinCEN requirements in the US, FCA in the UK, and similar authorities worldwide.
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 4 }} className="animate-on-scroll">
                    <VerifiedUserIcon sx={{ color: '#0070f3', mr: 2, mt: 0.5, flexShrink: 0 }} />
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>Fraud Prevention</Typography>
                      <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6 }}>
                        Our sophisticated monitoring systems detect and prevent fraudulent activities, keeping your funds safe from scammers.
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'flex-start' }} className="animate-on-scroll">
                    <VerifiedUserIcon sx={{ color: '#0070f3', mr: 2, mt: 0.5, flexShrink: 0 }} />
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>Consumer Protection</Typography>
                      <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6 }}>
                        Your rights as a consumer are protected under various financial regulations, giving you peace of mind when using our services.
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* Data Protection Section */}
      <Box sx={{ 
        py: { xs: 6, md: 14 },
        backgroundColor: 'rgba(10, 10, 10, 0.8)',
        borderTop: '1px solid rgba(255,255,255,0.05)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}>
        <Container maxWidth="lg" sx={{ px: { xs: 3, md: 3 } }}>
          <Typography variant="h3" className="animate-on-scroll" sx={{ textAlign: 'center', mb: 8, fontWeight: 700, fontSize: { xs: '1.8rem', md: '2.5rem' } }}>
            Your Data, Your Privacy
          </Typography>
          
          <Grid container spacing={6}>
            <Grid item xs={12} md={4} className="animate-on-scroll">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                  <PrivacyTipIcon sx={{ color: '#0070f3', fontSize: '3rem' }} />
                </Box>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2, textAlign: 'center' }}>
                  Encrypted Personal Data
                </Typography>
                <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6, textAlign: 'center' }}>
                  All your personal data, including identification documents and financial information, is stored with end-to-end encryption.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4} className="animate-on-scroll">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                  <ShieldIcon sx={{ color: '#0070f3', fontSize: '3rem' }} />
                </Box>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2, textAlign: 'center' }}>
                  No Data Selling
                </Typography>
                <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6, textAlign: 'center' }}>
                  Unlike many financial services, we never sell your data to third parties. Your information is used only to provide and improve our services.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4} className="animate-on-scroll">
              <Box sx={{ 
                p: 4, 
                height: '100%',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(30, 30, 30, 0.4)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                  <SecurityIcon sx={{ color: '#0070f3', fontSize: '3rem' }} />
                </Box>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2, textAlign: 'center' }}>
                  Self-Service Controls
                </Typography>
                <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6, textAlign: 'center' }}>
                  Access controls to view, download, and manage your data at any time. You're always in control of your personal information.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
      
      {/* CTA Section */}
      <Box sx={{ 
        py: { xs: 8, md: 16 },
        backgroundImage: 'linear-gradient(to right, rgba(25, 25, 25, 0.9), rgba(35, 35, 35, 0.9))',
        borderTop: '1px solid rgba(255,255,255,0.1)',
      }}>
        <Container maxWidth="md" sx={{ textAlign: 'center', px: { xs: 3, md: 3 } }}>
          <Typography 
            variant="h3" 
            className="animate-on-scroll"
            sx={{ mb: 3, fontWeight: 700 }}
          >
            Your Secure Digital Wallet
          </Typography>
          <Typography 
            variant="body1" 
            className="animate-on-scroll"
            sx={{ mb: 5, color: 'rgba(255,255,255,0.8)', maxWidth: '600px', mx: 'auto', fontSize: '1.1rem' }}
          >
            Join thousands who trust Liquicity with their cross-border payments, knowing their money and data are protected.
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4 }} className="animate-on-scroll">
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

/* Update animation CSS to apply to more element types and have a sequence effect */
const style = document.createElement('style');
style.innerHTML = `
  .animate-on-scroll {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
  }
  
  .animate-on-scroll.animated {
    opacity: 1;
    transform: translateY(0);
  }
  
  /* Add animation delay for consecutive items */
  .animate-on-scroll:nth-child(2) {
    transition-delay: 0.1s;
  }
  
  .animate-on-scroll:nth-child(3) {
    transition-delay: 0.2s;
  }
  
  .animate-on-scroll:nth-child(4) {
    transition-delay: 0.3s;
  }
`;
document.head.appendChild(style);

export default Security; 