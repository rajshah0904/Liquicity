import React, { createContext, useContext, useMemo } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';

// Create context
const ThemeContext = createContext();

export const useThemeMode = () => {
  return useContext(ThemeContext);
};

// Define theme settings - light mode
const getThemeOptions = () => ({
  palette: {
    mode: 'light',
    primary: {
      main: '#1e40af',
      light: '#3b82f6',
      dark: '#1565c0',
    },
    secondary: {
      main: '#37b24d',
      light: '#51cf66',
      dark: '#2f9e44',
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
    text: {
      primary: '#000000',
      secondary: '#666666',
    },
  },
  typography: {
    fontFamily: '"Sora", "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif',
    h1: { fontWeight: 700 },
    h2: { fontWeight: 700 },
    h3: { fontWeight: 600 },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 500 },
    h6: { fontWeight: 500 },
    button: {
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          boxShadow: 'none',
          borderBottom: '1px solid #e5e7eb',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#ffffff',
          borderRight: '1px solid #e5e7eb',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.05)',
        },
      },
    },
  },
});

// Theme provider component
export const CustomThemeProvider = ({ children }) => {
  // Always use light mode
  const themeMode = 'light';
  
  // Create light theme
  const theme = useMemo(() => createTheme(getThemeOptions()), []);

  // Simplified value object without toggle function
  const value = {
    themeMode
  };

  return (
    <ThemeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeContext; 