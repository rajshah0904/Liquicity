import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1e40af',
      light: '#3b82f6',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#0ea5e9',
      light: '#38bdf8',
      dark: '#0369a1',
      contrastText: '#ffffff',
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
    text: {
      primary: '#0f172a',
      secondary: '#475569',
    },
    divider: 'rgba(2, 6, 23, 0.08)',
    success: { main: '#16a34a' },
    error: { main: '#dc2626' },
    warning: { main: '#f59e0b' },
    info: { main: '#2563eb' },
  },
  typography: {
    fontFamily: '"Sora", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.2 },
    h2: { fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.01em', lineHeight: 1.2 },
    h3: { fontSize: '1.75rem', fontWeight: 600, letterSpacing: '-0.01em', lineHeight: 1.3 },
    h4: { fontSize: '1.5rem', fontWeight: 600 },
    h5: { fontSize: '1.25rem', fontWeight: 600 },
    h6: { fontSize: '1rem', fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCssBaseline: {
      styleOverrides: `
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        html, body { height: 100%; margin: 0; padding: 0; background:#ffffff; color:#0f172a; font-family:'Sora', sans-serif; }
        #root { height: 100%; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: rgba(150, 150, 150, 0.35); border-radius: 3px; }
        ::selection { background: rgba(37, 99, 235, 0.25); }
      `,
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 10, textTransform: 'none' },
        contained: {
          background: 'linear-gradient(180deg, #3b82f6 0%, #1e40af 100%)',
          color: '#fff',
        },
        outlined: { borderColor: '#3b82f6', color: '#1e40af' },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          boxShadow: '0 8px 24px rgba(2, 6, 23, 0.06)',
        },
      },
    },
    MuiPaper: { styleOverrides: { root: { background: '#ffffff' } } },
    MuiAppBar: { styleOverrides: { root: { background: '#ffffff' } } },
    MuiDrawer: { styleOverrides: { paper: { background: '#ffffff', color: '#333' } } },
    MuiDivider: { styleOverrides: { root: { borderColor: 'rgba(2, 6, 23, 0.08)' } } },
  },
});

export default theme;