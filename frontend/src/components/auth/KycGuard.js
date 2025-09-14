import { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';

const KycGuard = ({ children }) => {
  const { getAccessTokenSilently, isAuthenticated, isLoading, user } = useAuth0();
  const [allowed, setAllowed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const check = async () => {
      // Avoid any redirects while auth is loading to prevent flicker/loops
      if (isLoading) return;

      if (!isAuthenticated) {
        // Only redirect to login when definitely unauthenticated
        navigate('/login');
        return;
      }
      try {
        const token = await getAccessTokenSilently({
          authorizationParams: { scope: 'openid profile email' }
        });
        const res = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });
        const { exists, next_step } = res.data;
        if (!exists) {
          // Try auto-registration if we have an email; then allow KYC page without redirecting to signup
          try {
            if (user?.email) {
              await api.post('/onboard/register', { email: user.email }, { headers: { Authorization: `Bearer ${token}` } });
              localStorage.setItem('isNewSignup', 'true');
              setAllowed(true);
              return;
            }
          } catch (regErr) {
            if (regErr?.response?.status === 409) {
              setAllowed(true);
              return;
            }
          }
          navigate('/signup?noaccount=true');
          return;
        }
        if (next_step === 'done') {
          navigate('/dashboard');
          return;
        }
        setAllowed(true);
      } catch (e) {
        console.error('KycGuard error', e);
        // Do not bounce back to login on transient token/API errors; keep guard not allowed
        setAllowed(false);
      }
    };
    check();
  }, [isAuthenticated, isLoading, getAccessTokenSilently, navigate, user]);

  return allowed ? children : null;
};

export default KycGuard; 