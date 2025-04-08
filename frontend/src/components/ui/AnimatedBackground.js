import React from 'react';
import { Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const BackgroundContainer = styled(Box)(({ theme }) => ({
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: -1,
  background: '#000000', // Pure black background
}));

const AnimatedBackground = () => {
  return (
    <BackgroundContainer />
  );
};

export default AnimatedBackground; 