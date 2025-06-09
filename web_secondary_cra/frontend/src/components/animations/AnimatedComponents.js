import React from 'react';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';
import { Box, Card, Button, Paper, Typography, Container } from '@mui/material';

// Animation variants for different components
const fadeIn = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.6 }
  }
};

const slideUp = {
  hidden: { opacity: 0, y: 50 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { type: 'spring', damping: 20, stiffness: 300 }
  }
};

const slideRight = {
  hidden: { opacity: 0, x: -50 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { type: 'spring', damping: 25, stiffness: 300 }
  }
};

const scaleUp = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { 
    opacity: 1, 
    scale: 1,
    transition: { type: 'spring', damping: 20, stiffness: 300 }
  }
};

const staggeredChildren = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: "beforeChildren",
      staggerChildren: 0.2
    }
  }
};

// Styled components using framer-motion
export const MotionContainer = styled(motion(Container))(({ theme }) => ({
  overflow: 'hidden',
}));

export const MotionBox = styled(motion(Box))(({ theme }) => ({
  overflow: 'hidden',
}));

export const MotionCard = styled(motion(Card))(({ theme }) => ({
  overflow: 'hidden',
  borderRadius: theme.shape.borderRadius * 2,
  background: 'linear-gradient(135deg, #1F252E 0%, #2A3341 100%)',
  backdropFilter: 'blur(10px)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 12px 48px rgba(0, 0, 0, 0.3)',
  },
}));

export const MotionPaper = styled(motion(Paper))(({ theme }) => ({
  overflow: 'hidden',
  borderRadius: theme.shape.borderRadius * 1.5,
}));

export const MotionButton = styled(motion(Button))(() => ({
  overflow: 'hidden',
  // Using theme settings from the main theme
}));

export const MotionTypography = styled(motion(Typography))(() => ({
  // Typography inherits the theme settings
}));

// Reusable animated components with predefined variants
export const FadeInBox = ({ children, delay = 0, ...props }) => (
  <MotionBox
    initial="hidden"
    animate="visible"
    variants={fadeIn}
    transition={{ delay }}
    {...props}
  >
    {children}
  </MotionBox>
);

export const SlideUpBox = ({ children, delay = 0, ...props }) => (
  <MotionBox
    initial="hidden"
    animate="visible"
    variants={slideUp}
    transition={{ delay }}
    {...props}
  >
    {children}
  </MotionBox>
);

export const SlideRightBox = ({ children, delay = 0, ...props }) => (
  <MotionBox
    initial="hidden"
    animate="visible"
    variants={slideRight}
    transition={{ delay }}
    {...props}
  >
    {children}
  </MotionBox>
);

export const ScaleUpBox = ({ children, delay = 0, ...props }) => (
  <MotionBox
    initial="hidden"
    animate="visible"
    variants={scaleUp}
    transition={{ delay }}
    {...props}
  >
    {children}
  </MotionBox>
);

export const AnimatedCard = ({ children, delay = 0, ...props }) => (
  <MotionCard
    initial="hidden"
    animate="visible"
    variants={scaleUp}
    transition={{ delay }}
    {...props}
  >
    {children}
  </MotionCard>
);

export const AnimatedButton = ({ children, whileHover = { scale: 1.05 }, whileTap = { scale: 0.95 }, ...props }) => (
  <MotionButton
    initial="hidden"
    animate="visible"
    variants={fadeIn}
    whileHover={whileHover}
    whileTap={whileTap}
    {...props}
  >
    {children}
  </MotionButton>
);

export const AnimatedTypography = ({ children, delay = 0, variant, ...props }) => (
  <MotionTypography
    initial="hidden"
    animate="visible"
    variants={fadeIn}
    transition={{ delay }}
    variant={variant}
    {...props}
  >
    {children}
  </MotionTypography>
);

export const StaggerContainer = ({ children, ...props }) => (
  <MotionBox
    initial="hidden"
    animate="visible"
    variants={staggeredChildren}
    {...props}
  >
    {children}
  </MotionBox>
);

export const StaggerItem = ({ children, ...props }) => (
  <MotionBox
    variants={slideUp}
    {...props}
  >
    {children}
  </MotionBox>
);

// Page transition for react-router
export const pageTransition = {
  initial: {
    opacity: 0,
    y: 20
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.6, -0.05, 0.01, 0.99]
    }
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
      ease: [0.6, -0.05, 0.01, 0.99]
    }
  }
};

export default {
  fadeIn,
  slideUp,
  slideRight,
  scaleUp,
  staggeredChildren,
  pageTransition,
  MotionBox,
  MotionCard,
  MotionPaper,
  MotionButton,
  MotionTypography,
  FadeInBox,
  SlideUpBox,
  SlideRightBox,
  ScaleUpBox,
  AnimatedCard,
  AnimatedButton,
  AnimatedTypography,
  StaggerContainer,
  StaggerItem
}; 