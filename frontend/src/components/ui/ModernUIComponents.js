import React from 'react';
import { styled, keyframes } from '@mui/material/styles';
import { Box, Card, Button, Typography, Avatar, Container, Divider, Chip, IconButton } from '@mui/material';
import { motion } from 'framer-motion';

// Animations
const pulseAnimation = keyframes`
  0% { opacity: 0.3; }
  50% { opacity: 0.7; }
  100% { opacity: 0.3; }
`;

const floatAnimation = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
`;

const glowAnimation = keyframes`
  0% { box-shadow: 0 0 5px rgba(255,255,255,0.5); }
  50% { box-shadow: 0 0 20px rgba(255,255,255,0.5); }
  100% { box-shadow: 0 0 5px rgba(255,255,255,0.5); }
`;

// Futuristic Card Component
export const FuturisticCard = styled(Card)(({ theme }) => ({
  background: '#000000',
  borderRadius: 0,
  border: '1px solid rgba(255, 255, 255, 0.1)',
  padding: theme.spacing(3),
  boxShadow: 'none',
  transition: 'all 0.3s ease',
  overflow: 'hidden',
  position: 'relative',
  '&:hover': {
    boxShadow: 'none',
    transform: 'none',
  },
}));

// Neon Button
export const NeonButton = styled(Button)(({ theme }) => ({
  background: '#000000',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  color: '#FFFFFF',
  boxShadow: 'none',
  borderRadius: 0,
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
    boxShadow: 'none',
    border: '1px solid rgba(255, 255, 255, 0.2)',
  },
}));

// Animated Background Container
export const AnimatedBackground = () => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: '#000000',
        overflow: 'hidden',
        zIndex: -1,
      }}
    />
  );
};

// Floating Dots Background
export const FloatingDots = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  overflow: 'hidden',
  zIndex: 0,
  pointerEvents: 'none',
}));

// Glowing Text
export const GlowingText = styled(Typography)(({ theme }) => ({
  color: '#FFFFFF',
  textShadow: 'none',
  fontWeight: 600,
}));

// Floating Card
export const FloatingCard = styled(motion.div)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  background: '#000000',
  borderRadius: 0,
  border: '1px solid rgba(255, 255, 255, 0.08)',
  boxShadow: 'none',
  overflow: 'hidden',
  height: '100%',
}));

// Glass Container
export const GlassContainer = styled(Box)(({ theme }) => ({
  background: '#000000',
  borderRadius: 0,
  border: '1px solid rgba(255, 255, 255, 0.05)',
  padding: theme.spacing(3),
  boxShadow: 'none',
}));

// Gradient Border
export const GradientBorder = styled(Box)(({ theme }) => ({
  background: '#000000',
  borderRadius: 0,
  position: 'relative',
  padding: '1px',
  overflow: 'hidden',
  border: '1px solid rgba(255, 255, 255, 0.1)',
}));

// Futuristic Divider
export const FuturisticDivider = styled(Divider)(({ theme }) => ({
  border: 'none',
  height: '1px',
  margin: theme.spacing(3, 0),
  background: 'rgba(255, 255, 255, 0.1)',
}));

// Animated Chip
export const AnimatedChip = styled(Chip)(({ theme }) => ({
  background: '#000000',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  color: '#FFFFFF',
  borderRadius: 0,
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
    transform: 'none',
    boxShadow: 'none',
  },
}));

// Futuristic Avatar
export const FuturisticAvatar = styled(Avatar)(({ theme }) => ({
  border: '1px solid rgba(255, 255, 255, 0.2)',
  boxShadow: 'none',
  borderRadius: 0,
}));

// Gradient Text
export const GradientText = styled(Typography)(({ theme }) => ({
  color: '#FFFFFF',
  fontWeight: 700,
}));

// Glass Icon Button
export const GlassIconButton = styled(IconButton)(({ theme }) => ({
  background: '#000000',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  color: '#FFFFFF',
  borderRadius: 0,
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
    boxShadow: 'none',
    transform: 'none',
  },
}));

// Gradient Chip
export const GradientChip = styled(Chip)(({ theme }) => ({
  background: '#000000',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  color: '#FFFFFF',
  borderRadius: 0,
  fontWeight: 500,
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
    boxShadow: 'none',
    transform: 'none',
  },
}));

// Gradient Divider
export const GradientDivider = styled(Divider)(({ theme }) => ({
  border: 'none',
  height: '1px',
  background: 'rgba(255, 255, 255, 0.1)',
  margin: theme.spacing(3, 0),
})); 