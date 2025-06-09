import React from 'react';
import { Box, useTheme } from '@mui/material';
import { motion } from 'framer-motion';

const AnimatedBackground = () => {
  const theme = useTheme();
  
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: -1,
        overflow: 'hidden',
        background: '#000000'
      }}
    >
      {/* Subtle gradient overlay */}
      <Box 
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 20%, rgba(41, 41, 41, 0.8) 0%, rgba(0, 0, 0, 0.8) 100%)',
          opacity: 0.8
        }}
      />
      
      {/* Animated orbs */}
      <motion.div
        style={{
          position: 'absolute',
          width: '80vmax',
          height: '80vmax',
          borderRadius: '50%',
          background: `radial-gradient(circle at center, ${theme.palette.primary.dark} 0%, rgba(0,0,0,0) 70%)`,
          opacity: 0.05,
          top: '20%',
          right: '-20%',
        }}
        animate={{
          x: [0, 40, 0],
          y: [0, 30, 0],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />
      
      <motion.div
        style={{
          position: 'absolute',
          width: '60vmax',
          height: '60vmax',
          borderRadius: '50%',
          background: `radial-gradient(circle at center, ${theme.palette.secondary.dark} 0%, rgba(0,0,0,0) 70%)`,
          opacity: 0.05,
          bottom: '-10%',
          left: '-10%',
        }}
        animate={{
          x: [0, -30, 0],
          y: [0, 40, 0],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />
      
      {/* Grid overlay for depth */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `linear-gradient(rgba(25, 25, 25, 0.02) 1px, transparent 1px), 
                       linear-gradient(90deg, rgba(25, 25, 25, 0.02) 1px, transparent 1px)`,
          backgroundSize: '50px 50px',
        }}
      />
    </Box>
  );
};

export default AnimatedBackground; 