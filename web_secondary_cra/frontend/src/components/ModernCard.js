import React from 'react';
import { Card, CardContent, Typography, Box, IconButton } from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';

const StyledCard = styled(Card)(({ theme }) => ({
  position: 'relative',
  overflow: 'hidden',
  borderRadius: '16px',
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.3)',
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%)',
    zIndex: 1,
  },
}));

const GlowEffect = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'radial-gradient(circle at 50% 0%, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 50%)',
  opacity: 0.5,
  transition: 'opacity 0.3s ease',
  '&:hover': {
    opacity: 0.8,
  },
}));

const ContentWrapper = styled(Box)(({ theme }) => ({
  position: 'relative',
  zIndex: 2,
  padding: theme.spacing(3),
}));

const ModernCard = ({ 
  title, 
  subtitle, 
  content, 
  icon, 
  onClick,
  animationDelay = 0 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: animationDelay, duration: 0.5 }}
    >
      <StyledCard onClick={onClick}>
        <GlowEffect />
        <ContentWrapper>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {icon && (
              <IconButton
                sx={{
                  mr: 2,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  },
                }}
              >
                {icon}
              </IconButton>
            )}
            <Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  color: '#FFFFFF',
                  mb: 0.5,
                }}
              >
                {title}
              </Typography>
              {subtitle && (
                <Typography
                  variant="body2"
                  sx={{
                    color: 'rgba(255, 255, 255, 0.7)',
                  }}
                >
                  {subtitle}
                </Typography>
              )}
            </Box>
          </Box>
          <Typography
            variant="body1"
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              lineHeight: 1.6,
            }}
          >
            {content}
          </Typography>
        </ContentWrapper>
      </StyledCard>
    </motion.div>
  );
};

export default ModernCard; 