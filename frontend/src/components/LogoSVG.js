import React from 'react';

const LogoSVG = ({ color = '#FFFFFF', size = 80 }) => {
  return (
    <img 
      src="/images/liquicity_logo.png"
      alt="Liquicity Logo"
      width={size}
      height={size}
      style={{ 
        objectFit: 'contain',
        transform: 'scale(1.5)',
        transformOrigin: 'center'
      }}
    />
  );
};

export default LogoSVG; 