import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  AppBar,
  Toolbar,
  Fade,
} from '@mui/material';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import LogoSVG from './LogoSVG';

const ScrollHeader = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 50;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [scrolled]);
  
  const isActive = (path) => {
    // Treat both root and /home as the same page for active link highlighting
    if (path === '/' || path === '/home') {
      return location.pathname === '/' || location.pathname === '/home';
    }
    return location.pathname === path;
  };
  
  // Link styling based on active state
  const getLinkStyles = (path) => ({
    mx: { xs: 1.5, sm: 2.5 }, 
    fontSize: { xs: '0.85rem', sm: '0.95rem' },
    color: 'inherit',
    textDecoration: 'none',
    position: 'relative',
    '&::after': isActive(path) ? {
      content: '""',
      position: 'absolute',
      bottom: -4,
      left: 0,
      width: '100%',
      height: '2px',
      backgroundColor: '#fff',
      display: 'block'
    } : { display: 'none' },
    '&:hover::after': {
      content: '""',
      position: 'absolute',
      bottom: -4,
      left: 0,
      width: '100%',
      height: '2px',
      backgroundColor: 'rgba(255, 255, 255, 0.7)',
      display: 'block'
    }
  });
  
  return (
    <AppBar 
      position="fixed" 
      elevation={0}
      sx={{ 
        background: scrolled ? 'rgba(0, 0, 0, 0.8)' : 'transparent',
        backdropFilter: scrolled ? 'blur(10px)' : 'none',
        boxShadow: scrolled ? '0 4px 20px rgba(0,0,0,0.2)' : 'none',
        py: 1.5,
        transition: 'all 0.3s ease',
        zIndex: 1100,
      }}
    >
      <Container maxWidth="lg" sx={{ px: { xs: 2, md: 3 } }}>
        <Toolbar disableGutters sx={{ px: 0, display: 'flex', justifyContent: 'center' }}>
          {/* Logo Section */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            position: 'absolute', 
            left: { xs: 8, sm: 16, md: 24 },
            width: { xs: '80px', sm: 'auto' }
          }}>
            <Box className="logo-container">
              {/* Logo for scrolled state */}
              <Fade in={scrolled} timeout={300}>
                <Box 
                  className="logo-image"
                  sx={{ 
                    position: 'absolute',
                    opacity: scrolled ? 1 : 0,
                    display: 'flex',
                    alignItems: 'center',
                    cursor: 'pointer',
                    zIndex: 10,
                  }}
                  onClick={() => navigate('/')}
                >
                  <LogoSVG size={48} color="#ffffff" />
                </Box>
              </Fade>
              
              {/* Text Logo for non-scrolled state */}
              <Fade in={!scrolled} timeout={300}>
                <Typography 
                  variant="h5" 
                  className="logo-text liquicity-logo"
                  sx={{ 
                    fontWeight: 700,
                    letterSpacing: '-0.5px',
                    opacity: scrolled ? 0 : 1,
                    fontSize: { xs: '1.3rem', sm: '1.5rem', md: '1.8rem' },
                    cursor: 'pointer',
                    zIndex: 10,
                  }}
                  onClick={() => navigate('/')}
                >
                  Liquicity
                </Typography>
              </Fade>
            </Box>
          </Box>
          
          {/* Centered Navigation Tabs */}
          <Box 
            className="header-center-tabs"
            sx={{ 
              transition: 'all 0.3s ease',
              opacity: scrolled ? 0 : 1,
              pointerEvents: scrolled ? 'none' : 'auto',
              display: 'flex',
              justifyContent: 'center',
              paddingLeft: { xs: 0, sm: 0 },
              marginLeft: { xs: 'auto', sm: 0 },
              marginRight: { xs: 'auto', sm: 0 },
              width: '100%',
              maxWidth: { xs: '220px', sm: 'none' },
              flexWrap: { xs: 'wrap', sm: 'nowrap' },
              '& > a': {
                display: 'inline-block',
                whiteSpace: 'nowrap',
                textAlign: 'center',
              }
            }}
          >
            <RouterLink to="/" className={isActive('/') ? 'active' : ''} style={{ textDecoration: 'none' }}>
              <Box component="span" sx={getLinkStyles('/')}>
                Home
              </Box>
            </RouterLink>
            
            <RouterLink to="/how-it-works" className={isActive('/how-it-works') ? 'active' : ''} style={{ textDecoration: 'none' }}>
              <Box component="span" sx={getLinkStyles('/how-it-works')}>
                How it works
              </Box>
            </RouterLink>
            
            <RouterLink to="/security" className={isActive('/security') ? 'active' : ''} style={{ textDecoration: 'none' }}>
              <Box component="span" sx={getLinkStyles('/security')}>
                Security
              </Box>
            </RouterLink>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default ScrollHeader; 