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
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
`;

const glowAnimation = keyframes`
  0% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
  50% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }
  100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
`;

// Futuristic Card Component
export const FuturisticCard = styled(Card)(({ theme }) => ({
  background: '#111827',
  borderRadius: 16,
  border: '1px solid rgba(55, 65, 81, 0.5)',
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
  background: 'linear-gradient(45deg, #3b82f6 30%, #2563eb 90%)',
  color: '#FFFFFF',
  fontWeight: 600,
  padding: '10px 20px',
  borderRadius: 8,
  border: 'none',
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s ease',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
    transition: 'all 0.5s ease',
  },
  '&:hover': {
    boxShadow: '0 0 15px rgba(59, 130, 246, 0.5), 0 0 30px rgba(59, 130, 246, 0.3)',
    transform: 'translateY(-2px)',
    '&::before': {
      left: '100%',
    },
  },
  '&:active': {
    transform: 'scale(0.98)',
  },
}));

// Animated Background Container
export const AnimatedBackground = styled(Box)(({ theme }) => ({
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: -1,
  background: '#000000',
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'url("data:image/svg+xml,%3Csvg width=\'100%25\' height=\'100%25\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cdefs%3E%3Cpattern id=\'grid\' width=\'40\' height=\'40\' patternUnits=\'userSpaceOnUse\'%3E%3Cpath d=\'M 40 0 L 0 0 0 40\' fill=\'none\' stroke=\'rgba(59, 130, 246, 0.05)\' stroke-width=\'0.5\'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width=\'100%25\' height=\'100%25\' fill=\'url(%23grid)\'/%3E%3C/svg%3E")',
    opacity: 0.2,
  },
}));

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
export const FloatingCard = styled(Card)(({ theme }) => ({
  background: 'rgba(17, 24, 39, 0.5)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(55, 65, 81, 0.6)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  borderRadius: 16,
  transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '1px',
    background: 'linear-gradient(90deg, rgba(59,130,246,0) 0%, rgba(59,130,246,0.4) 50%, rgba(59,130,246,0) 100%)',
    zIndex: 1,
  },
  '&:hover': {
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.25), 0 0 15px rgba(59, 130, 246, 0.15)',
    transform: 'translateY(-4px)',
    border: '1px solid rgba(59, 130, 246, 0.2)',
    '&::before': {
      animation: 'glow 1.5s ease-in-out infinite',
    },
  },
  '@keyframes glow': {
    '0%': {
      opacity: 0.3,
      background: 'linear-gradient(90deg, rgba(59,130,246,0) 0%, rgba(59,130,246,0.4) 50%, rgba(59,130,246,0) 100%)',
    },
    '50%': {
      opacity: 0.7,
      background: 'linear-gradient(90deg, rgba(59,130,246,0) 0%, rgba(59,130,246,0.7) 50%, rgba(59,130,246,0) 100%)',
    },
    '100%': {
      opacity: 0.3,
      background: 'linear-gradient(90deg, rgba(59,130,246,0) 0%, rgba(59,130,246,0.4) 50%, rgba(59,130,246,0) 100%)',
    },
  },
}));

// Glass Container
export const GlassContainer = styled(Box)(({ theme }) => ({
  background: 'rgba(17, 24, 39, 0.5)', 
  backdropFilter: 'blur(10px)',
  borderRadius: 16,
  border: '1px solid rgba(55, 65, 81, 0.6)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  padding: theme.spacing(3),
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2), 0 0 15px rgba(59, 130, 246, 0.1)',
    borderColor: 'rgba(59, 130, 246, 0.2)',
  },
}));

// Gradient Border
export const GradientBorder = styled(Box)(({ theme }) => ({
  position: 'relative',
  padding: 2,
  borderRadius: 16,
  background: 'linear-gradient(45deg, #3b82f6, #2563eb)',
  '& > *': {
    borderRadius: 14,
  },
}));

// Futuristic Divider
export const FuturisticDivider = styled(Divider)(({ theme }) => ({
  border: 'none',
  height: '1px',
  margin: theme.spacing(3, 0),
  background: 'rgba(55, 65, 81, 0.6)',
}));

// Animated Chip
export const AnimatedChip = styled(Chip)(({ theme }) => ({
  background: '#111827',
  border: '1px solid rgba(55, 65, 81, 0.6)',
  color: '#FFFFFF',
  borderRadius: 8,
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'rgba(59, 130, 246, 0.1)',
    borderColor: 'rgba(59, 130, 246, 0.3)',
    transform: 'translateY(-2px)',
  },
}));

// Futuristic Avatar
export const FuturisticAvatar = styled(Avatar)(({ theme }) => ({
  border: '2px solid rgba(59, 130, 246, 0.4)',
  boxShadow: '0 0 10px rgba(59, 130, 246, 0.2)',
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: '0 0 15px rgba(59, 130, 246, 0.3)',
    transform: 'scale(1.05)',
  },
}));

// Gradient Text
export const GradientText = styled(Typography)(({ theme, gradient }) => ({
  background: gradient || 'linear-gradient(45deg, #3b82f6 30%, #60a5fa 90%)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  display: 'inline-block',
}));

// Glass Icon Button
export const GlassIconButton = styled(IconButton)(({ theme }) => ({
  background: 'rgba(59, 130, 246, 0.1)',
  backdropFilter: 'blur(8px)',
  border: '1px solid rgba(59, 130, 246, 0.2)',
  borderRadius: '50%',
  color: theme.palette.text.primary,
  transition: 'all 0.3s ease',
  '&:hover': {
    background: 'rgba(59, 130, 246, 0.2)',
    borderColor: 'rgba(59, 130, 246, 0.4)',
    boxShadow: '0 0 15px rgba(59, 130, 246, 0.2)',
    transform: 'scale(1.05)',
  },
}));

// Gradient Chip
export const GradientChip = styled(Chip)(({ theme, color = 'primary' }) => {
  const getGradient = () => {
    switch (color) {
      case 'success':
        return 'linear-gradient(45deg, #10b981 30%, #059669 90%)';
      case 'error':
        return 'linear-gradient(45deg, #ef4444 30%, #dc2626 90%)';
      case 'warning':
        return 'linear-gradient(45deg, #f59e0b 30%, #d97706 90%)';
      case 'info':
        return 'linear-gradient(45deg, #00b0ff 30%, #0091ea 90%)';
      default:
        return 'linear-gradient(45deg, #3b82f6 30%, #2563eb 90%)';
    }
  };

  return {
    background: getGradient(),
    color: '#000',
    fontWeight: 600,
    border: 'none',
    boxShadow: `0 0 10px ${theme.palette[color]?.main || theme.palette.primary.main}40`,
    '&:hover': {
      boxShadow: `0 0 15px ${theme.palette[color]?.main || theme.palette.primary.main}60`,
    },
  };
});

// Gradient Divider
export const GradientDivider = styled(Divider)(({ theme }) => ({
  background: 'linear-gradient(90deg, rgba(0,229,255,0) 0%, rgba(0,229,255,0.5) 50%, rgba(0,229,255,0) 100%)',
  height: '1px',
  margin: theme.spacing(3, 0),
}));

export default {
  FloatingCard,
  NeonButton,
  GradientBorder,
  GradientDivider,
  GradientChip,
  GlassIconButton,
  GradientText,
  AnimatedBackground,
  FuturisticAvatar,
  GlassContainer,
}; 