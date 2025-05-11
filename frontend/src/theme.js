import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3b82f6',  // Bright blue - matches the image
      light: '#60a5fa',
      dark: '#2563eb',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#8b5cf6',  // Purple - tech feel
      light: '#a78bfa',
      dark: '#7c3aed',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#000000',  // Pure black background
      paper: 'rgba(17, 24, 39, 0.8)',  // Very dark blue-black with transparency
    },
    text: {
      primary: '#FFFFFF',
      secondary: 'rgba(255, 255, 255, 0.7)',
      disabled: 'rgba(255, 255, 255, 0.38)',
    },
    divider: 'rgba(255, 255, 255, 0.12)',
    error: {
      main: '#ef4444',  // Red from image
      light: '#f87171',
      dark: '#dc2626',
      contrastText: '#fff',
    },
    warning: {
      main: '#f59e0b',  // Amber
      light: '#fbbf24',
      dark: '#d97706',
      contrastText: '#000',
    },
    info: {
      main: '#3b82f6',  // Blue
      light: '#60a5fa',
      dark: '#2563eb',
      contrastText: '#fff',
    },
    success: {
      main: '#10b981',  // Green from image
      light: '#34d399',
      dark: '#059669',
      contrastText: '#fff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
      lineHeight: 1.2,
      background: 'linear-gradient(45deg, #00e5ff 30%, #00b0ff 90%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,
      letterSpacing: '-0.01em',
      lineHeight: 1.2,
      background: 'linear-gradient(45deg, #00e5ff 30%, #00b0ff 90%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
      lineHeight: 1.3,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
      lineHeight: 1.3,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      letterSpacing: '0',
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      letterSpacing: '0.02em',
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      letterSpacing: '0.01em',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      letterSpacing: '0.01em',
      lineHeight: 1.6,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      letterSpacing: '0.02em',
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
          box-sizing: border-box;
        }
        
        html, body {
          margin: 0;
          padding: 0;
          height: 100%;
          background-color: #000000;
          color: #FFFFFF;
          font-family: 'Inter', sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
          background: #000000;
        }
        
        #root {
          height: 100%;
        }
        
        ::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        
        ::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.03);
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
          background: rgba(59, 130, 246, 0.4);
          border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: rgba(59, 130, 246, 0.6);
        }
        
        ::selection {
          background: rgba(59, 130, 246, 0.3);
        }
      `,
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          padding: '8px 16px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 0 15px rgba(59, 130, 246, 0.3)',
          },
        },
        contained: {
          background: 'linear-gradient(45deg, #3b82f6 30%, #2563eb 90%)',
          color: '#fff',
          '&:hover': {
            background: 'linear-gradient(45deg, #60a5fa 20%, #3b82f6 100%)',
          },
        },
        outlined: {
          borderColor: '#3b82f6',
          color: '#3b82f6',
          '&:hover': {
            borderColor: '#60a5fa',
            boxShadow: '0 0 10px rgba(59, 130, 246, 0.3)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(17, 24, 39, 0.7)',
          backdropFilter: 'blur(10px)',
          borderRadius: 16,
          border: '1px solid rgba(59, 130, 246, 0.1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0 8px 32px rgba(59, 130, 246, 0.15)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
          }
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          background: 'rgba(17, 24, 39, 0.7)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s ease',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(59, 130, 246, 0.1)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'rgba(0, 0, 0, 0.9)',
          backdropFilter: 'blur(10px)',
          borderRight: '1px solid rgba(59, 130, 246, 0.1)',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          transition: 'all 0.2s ease',
          '&:hover': {
            background: 'rgba(0, 229, 255, 0.05)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.2)',
              transition: 'all 0.2s ease',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(0, 229, 255, 0.4)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#00e5ff',
              boxShadow: '0 0 10px rgba(0, 229, 255, 0.2)',
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(10px)',
        },
        filled: {
          background: 'rgba(0, 229, 255, 0.1)',
          border: '1px solid rgba(0, 229, 255, 0.2)',
        },
        outlined: {
          borderColor: 'rgba(0, 229, 255, 0.4)',
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          border: '2px solid rgba(0, 229, 255, 0.3)',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: 'rgba(0, 229, 255, 0.1)',
        },
      },
    },
  },
});

export default theme; 